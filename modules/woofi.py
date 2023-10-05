from .utils.contracts.abi import ABI_WOOFI_SWAP, ABI_WOOFI_BRIDGE
from .utils.contracts.contract import WOOFI_SWAP_CONTRACTS, WOOFI_PATH, LAYERZERO_CHAINS_ID, WOOFI_BRIDGE_CONTRACTS
from config import STR_CANCEL
from setting import Value_Woofi_Bridge, Value_Woofi_Swap
from .utils.helpers import list_send, decimalToInt, intToDecimal, round_to

from loguru import logger
from web3 import Web3
import random
from .utils.manager_async import Web3ManagerAsync

async def woofi_get_min_amount(web3, chain, from_token, to_token, value):

    slippage = 0.95

    try:
        if from_token.upper() != to_token.upper():
            contract = web3.eth.contract(address=web3.to_checksum_address(WOOFI_SWAP_CONTRACTS[chain]), abi=ABI_WOOFI_SWAP)
            minToAmount = await contract.functions.tryQuerySwap(
                Web3.to_checksum_address(from_token),
                Web3.to_checksum_address(to_token),
                value
                ).call()

            return int(minToAmount * slippage)
        else:
            return int(value)
    
    except Exception as error:
        logger.error(f'error : {error}. return 0')
        return 0

class WoofiBridge:
    
    def __init__(self, key, number, params=None):
        self.params = params
        if self.params:
            self.from_chain = self.params['from_chain']
            self.to_chain = self.params['to_chain']
            self.from_token = self.params['from_token']
            self.to_token = self.params['to_token']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.swap_all_balance = self.params['swap_all_balance']
            self.min_amount_swap = self.params['min_amount_swap']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
        else:
            self.from_chain = Value_Woofi_Bridge.from_chain
            self.to_chain = Value_Woofi_Bridge.to_chain
            self.from_token = Value_Woofi_Bridge.from_token
            self.to_token = Value_Woofi_Bridge.to_token
            self.amount_from = Value_Woofi_Bridge.amount_from
            self.amount_to = Value_Woofi_Bridge.amount_to
            self.swap_all_balance = Value_Woofi_Bridge.swap_all_balance
            self.min_amount_swap = Value_Woofi_Bridge.min_amount_swap
            self.keep_value_from = Value_Woofi_Bridge.keep_value_from
            self.keep_value_to = Value_Woofi_Bridge.keep_value_to
        self.key = key
        self.number = number

    async def setup(self):
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.web3_to_chain = Web3ManagerAsync(self.key, self.to_chain).web3
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, self.from_token, self.amount_from, self.amount_to)
        self.from_token_data = await self.manager.get_token_info(self.from_token)
        self.to_token_data = await self.manager.get_token_info(self.to_token)
        self.value = intToDecimal(self.amount, self.from_token_data['decimal']) 
        self.module_str = f'{self.number} {self.manager.address} | woofi_bridge : {self.from_chain} => {self.to_chain}'

    async def get_srcInfos(self):

        bridgeToken = WOOFI_PATH[self.from_chain]
        minBridgeAmount = await woofi_get_min_amount(self.manager.web3, self.from_chain, self.from_token_data['address'], WOOFI_PATH[self.from_chain], self.value)

        srcInfos = [
            self.from_token_data['address'], 
            Web3.to_checksum_address(bridgeToken),    
            self.value,        
            minBridgeAmount
        ]

        return srcInfos

    async def get_dstInfos(self, amount):

        minToAmount = int(await woofi_get_min_amount(self.web3_to_chain, self.to_chain, WOOFI_PATH[self.to_chain], self.to_token_data['address'], amount) * 0.99)
        bridgeToken = Web3.to_checksum_address(WOOFI_PATH[self.to_chain])

        dstInfos = [
            LAYERZERO_CHAINS_ID[self.to_chain], # chainId
            self.to_token_data['address'], # toToken
            bridgeToken,    # bridgeToken
            minToAmount,    # minToAmount
            0               # airdropNativeAmount
        ]

        return dstInfos

    async def get_txn(self):

        try:
            contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(WOOFI_BRIDGE_CONTRACTS[self.from_chain]), abi=ABI_WOOFI_BRIDGE)

            srcInfos = await self.get_srcInfos()
            if self.from_chain == 'bsc':
                amount_src = decimalToInt(srcInfos[3], 18)
                amount_src = intToDecimal(amount_src, 6)
            else:
                amount_src = srcInfos[3]
            dstInfos = await self.get_dstInfos(amount_src)

            if self.from_token != '':
                await self.manager.approve(self.value, self.from_token_data['address'], WOOFI_BRIDGE_CONTRACTS[self.from_chain])

            layerzero_fee = await contract.functions.quoteLayerZeroFee(
                random.randint(112101680502565000, 712101680502565000), # refId
                self.manager.address, # to
                srcInfos, 
                dstInfos
                ).call()
            layerzero_fee = int(layerzero_fee[0])

            if self.from_token == '':
                value = int(self.value + layerzero_fee)
            else:
                value = int(layerzero_fee)

            contract_txn = await contract.functions.crossSwap(
                random.randint(112101680502565000, 712101680502565000), # refId
                self.manager.address, # to
                srcInfos, 
                dstInfos
                ).build_transaction(
                {
                    'from': self.manager.address,
                    'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'value': value,
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.swap_all_balance and self.from_token == '':
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

class WoofiSwap:
    
    def __init__(self, key, number, params=None):
        self.key = key
        self.number = number
        self.params = params

    async def setup(self):
        if self.params:
            self.chain = self.params['chain']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
            self.swap_all_balance = self.params['swap_all_balance']
            self.from_token = self.params['from_token']
            self.to_token = self.params['to_token']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.min_amount_swap = self.params['min_amount_swap']
        else:
            self.chain = Value_Woofi_Swap.chain
            self.keep_value_from = Value_Woofi_Swap.keep_value_from
            self.keep_value_to = Value_Woofi_Swap.keep_value_to
            self.swap_all_balance = Value_Woofi_Swap.swap_all_balance
            self.from_token = Value_Woofi_Swap.from_token
            self.to_token = Value_Woofi_Swap.to_token
            self.amount_from = Value_Woofi_Swap.amount_from
            self.amount_to = Value_Woofi_Swap.amount_to
            self.min_amount_swap = Value_Woofi_Swap.min_amount_swap

        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, self.from_token, self.amount_from, self.amount_to)
        self.from_token_data = await self.manager.get_token_info(self.from_token)
        self.to_token_data = await self.manager.get_token_info(self.to_token)
        self.value = intToDecimal(self.amount, self.from_token_data['decimal']) 
        self.module_str = f'{self.number} {self.manager.address} | woofi_swap ({self.chain}) : {round_to(self.amount)} {self.from_token_data["symbol"]} => {self.to_token_data["symbol"]}'
        self.minToAmount = await woofi_get_min_amount(self.manager.web3, self.chain, self.from_token_data['address'], self.to_token_data['address'], self.value)

    async def get_txn(self):

        try:

            if self.from_token != '':
                await self.manager.approve(self.value, self.from_token_data['address'], WOOFI_SWAP_CONTRACTS[self.chain])

            if self.from_token == '':
                value = self.value
            else:
                value = 0

            contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(WOOFI_SWAP_CONTRACTS[self.chain]), abi=ABI_WOOFI_SWAP)

            contract_txn = await contract.functions.swap(
                self.from_token_data['address'], 
                self.to_token_data['address'], 
                int(self.value), 
                self.minToAmount, 
                self.manager.address,
                self.manager.address
            ).build_transaction(
                {
                    'from': self.manager.address,
                    'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'value': value,
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit(contract_txn)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.swap_all_balance and self.from_token == '':
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

