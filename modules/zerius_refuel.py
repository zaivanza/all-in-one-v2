from .utils.contracts.contract import  ZERIUS_REFUEL_CONTRACTS, LAYERZERO_CHAINS_ID
from config import STR_CANCEL, PRICES_NATIVE, ABI_ZERIUS_REFUEL
from setting import Value_Zerius_Refuel
from .utils.helpers import list_send, intToDecimal, decimalToInt, round_to
from .utils.files import call_json
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3
from termcolor import cprint
import random
import sys
from eth_account import Account
from eth_abi.packed import encode_packed

class ZeriusRefuel:
    
    def __init__(self, key, number, params=None):
        self.params = params
        if self.params:
            self.from_chain = self.params['from_chain']
            self.to_chain = self.params['to_chain']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.swap_all_balance = self.params['swap_all_balance']
            self.min_amount_swap = self.params['min_amount_swap']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
            self.get_layerzero_fee = self.params['get_layerzero_fee']
        else:
            self.from_chain = Value_Zerius_Refuel.from_chain
            self.to_chain = Value_Zerius_Refuel.to_chain
            self.amount_from = Value_Zerius_Refuel.amount_from
            self.amount_to = Value_Zerius_Refuel.amount_to
            self.swap_all_balance = Value_Zerius_Refuel.swap_all_balance
            self.min_amount_swap = Value_Zerius_Refuel.min_amount_swap
            self.keep_value_from = Value_Zerius_Refuel.keep_value_from
            self.keep_value_to = Value_Zerius_Refuel.keep_value_to
            self.get_layerzero_fee = Value_Zerius_Refuel.get_layerzero_fee
        self.key = key
        self.number = number

    async def setup(self):
        self.from_chain = random.choice(self.from_chain)
        self.to_chain = random.choice(self.to_chain)
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(ZERIUS_REFUEL_CONTRACTS[self.from_chain]), abi=ABI_ZERIUS_REFUEL)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, '', self.amount_from, self.amount_to)
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.adapterParams = await self.get_adapterParams(self.value)
        self.module_str = f'{self.number} {self.manager.address} | zerius_refuel : {self.from_chain} => {self.to_chain}'

        if self.get_layerzero_fee:
            await self.check_refuel_fees()

    async def get_adapterParams(self, amount: int):
        minDstGas = await self.get_min_dst_gas_lookup(LAYERZERO_CHAINS_ID[self.to_chain], 0)        
        addressOnDist = Account().from_key(self.key).address
        return encode_packed(
            ["uint16", "uint256", "uint256", "address"],
            [2, minDstGas, amount, addressOnDist] 
        )
    
    async def get_min_dst_gas_lookup(self, dstChainId, funcType):
        return await self.contract.functions.minDstGasLookup(dstChainId, funcType).call()

    async def get_txn(self):
        try:
            dst_contract_address = encode_packed(["address"], [ZERIUS_REFUEL_CONTRACTS[self.to_chain]])
            send_value = await self.contract.functions.estimateSendFee(LAYERZERO_CHAINS_ID[self.to_chain], dst_contract_address, self.adapterParams).call()

            contract_txn = await self.contract.functions.refuel(
                    LAYERZERO_CHAINS_ID[self.to_chain],
                    dst_contract_address,
                    self.adapterParams
                ).build_transaction(
                {
                    "from": self.manager.address,
                    "value": send_value[0],
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.swap_all_balance:
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

    async def check_refuel_fees(self):
        result = {}
        for from_chain in ZERIUS_REFUEL_CONTRACTS:
            result.update({from_chain:{}})
            adapterParams = await self.get_adapterParams(1)

            for to_chain in LAYERZERO_CHAINS_ID:
                if from_chain != to_chain:
                    try:
                        dst_contract_address = encode_packed(["address"], [ZERIUS_REFUEL_CONTRACTS[to_chain]])
                        send_value = await self.contract.functions.estimateSendFee(LAYERZERO_CHAINS_ID[to_chain], dst_contract_address, adapterParams).call()
                        
                        send_value = decimalToInt(send_value[0], 18)
                        send_value = round_to(send_value * PRICES_NATIVE[from_chain])
                        cprint(f'{from_chain} => {to_chain} : {send_value}', 'white')
                        result[from_chain].update({to_chain:send_value})
                    except Exception as error:
                        cprint(f'{from_chain} => {to_chain} : None', 'white')
                        result[from_chain].update({to_chain:None})

        path = 'results/zerius_refuel'
        call_json(result, path)
        cprint(f'\nResults written to file: {path}.json\n', 'blue')
        sys.exit()