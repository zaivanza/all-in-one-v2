from .utils.contracts.abi import ABI_SUSHISWAP
from .utils.contracts.contract import SUSHISWAP_CONTRACTS, WETH_CONTRACTS
from config import STR_CANCEL
from setting import Value_Sushiswap
from .utils.helpers import round_to, list_send, intToDecimal
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3
import time, random

class SushiSwap:

    def __init__(self, key, number, params=None):
        self.params = params
        if self.params:
            self.chain = self.params['chain']
            self.from_token_address = self.params['from_token']
            self.to_token_address = self.params['to_token']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.swap_all_balance = self.params['swap_all_balance']
            self.min_amount_swap = self.params['min_amount_swap']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
            self.slippage = self.params['slippage']
        else:
            self.chain = Value_Sushiswap.chain
            self.from_token_address = Value_Sushiswap.from_token
            self.to_token_address = Value_Sushiswap.to_token
            self.amount_from = Value_Sushiswap.amount_from
            self.amount_to = Value_Sushiswap.amount_to
            self.swap_all_balance = Value_Sushiswap.swap_all_balance
            self.min_amount_swap = Value_Sushiswap.min_amount_swap
            self.keep_value_from = Value_Sushiswap.keep_value_from
            self.keep_value_to = Value_Sushiswap.keep_value_to
            self.slippage = Value_Sushiswap.slippage
        self.key = key
        self.number = number

    async def setup(self):
        self.from_token_address = random.choice(self.from_token_address)
        self.to_token_address = random.choice(self.to_token_address)
        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.from_token_data = await self.manager.get_token_info(self.from_token_address)
        self.to_token_data = await self.manager.get_token_info(self.to_token_address)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, self.from_token_address, self.amount_from, self.amount_to)
        self.value = intToDecimal(self.amount, self.from_token_data['decimal']) 
        self.module_str = f'{self.number} {self.manager.address} | sushiswap ({self.chain}) : {round_to(self.amount)} {self.from_token_data["symbol"]} => {self.to_token_data["symbol"]}'

    async def get_amountOutMin(self, contract, from_token, to_token):

        contract_txn = await contract.functions.getAmountsOut(
            self.value,
            [from_token, to_token],
            ).call()

        return int(contract_txn[1] * (1 - self.slippage / 100))

    async def get_txn(self):

        try:

            if self.from_token_address != '':
                await self.manager.approve(self.value, self.from_token_data['address'], SUSHISWAP_CONTRACTS[self.chain])

            if self.from_token_address == '':
                value = self.value
            else:
                value = 0

            contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(SUSHISWAP_CONTRACTS[self.chain]), abi=ABI_SUSHISWAP)

            # weth => token
            if self.from_token_address == '':

                from_token  = Web3.to_checksum_address(WETH_CONTRACTS[self.chain])
                to_token    = self.to_token_data["address"]
                amountOut   = await self.get_amountOutMin(contract, from_token, to_token)

                contract_txn = await contract.functions.swapExactETHForTokens(
                    amountOut,
                    [from_token, to_token],
                    self.manager.address, # receiver
                    (int(time.time()) + 10000)  # deadline
                    ).build_transaction(
                    {
                        "from": self.manager.address,
                        "value": value,
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                        'gasPrice': 0,
                        'gas': 0,
                    }
                )

            # token => weth
            if self.to_token_address == '':

                from_token  = self.from_token_data["address"]
                to_token    = Web3.to_checksum_address(WETH_CONTRACTS[self.chain])
                amountOut   = await self.get_amountOutMin(contract, from_token, to_token)

                contract_txn = await contract.functions.swapExactTokensForETH(
                    value, # amountIn
                    amountOut, # amountOutMin
                    [from_token, to_token], # path
                    self.manager.address, # receiver
                    (int(time.time()) + 10000)  # deadline
                    ).build_transaction(
                    {
                        "from": self.manager.address,
                        "value": 0,
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                        'gasPrice': 0,
                        'gas': 0,
                    }
                )

            # token => token
            if (self.to_token_address != '' and self.from_token_address != ''):

                from_token  = self.from_token_data["address"]
                to_token    = self.to_token_data["address"]
                amountOut   = await self.get_amountOutMin(contract, from_token, to_token)

                contract_txn = await contract.functions.swapExactTokensForTokens(
                    value, # amountIn
                    amountOut, # amountOutMin
                    [from_token, to_token], # path
                    self.manager.address, # receiver
                    (int(time.time()) + 10000)  # deadline
                    ).build_transaction(
                    {
                        "from": self.manager.address,
                        "value": 0,
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                        'gasPrice': 0,
                        'gas': 0,
                    }
                )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.swap_all_balance and self.from_token_address == '':
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = contract_txn['value'] - gas_gas

            if self.amount >= self.min_amount_swap:
                return contract_txn
            else:
                logger.error(f"{self.module_str} | {self.amount} (amount) < {self.min_amount_swap} (min_amount_swap)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | {round_to(self.amount)} less {self.min_amount_swap}')
                return False
            
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} | {error}')
            return False




