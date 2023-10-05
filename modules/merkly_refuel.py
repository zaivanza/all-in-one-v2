from data.data import DATA
from .utils.contracts.abi import ABI_MERKLY_REFUEL
from .utils.contracts.contract import  MERKLY_CONTRACTS, LAYERZERO_CHAINS_ID
from config import STR_CANCEL, PRICES_NATIVE
from setting import Value_Merkly_Refuel
from .utils.helpers import list_send, intToDecimal, decimalToInt, round_to
from .utils.files import call_json
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3
from eth_abi import encode
from termcolor import cprint
import random
import sys

def get_adapterParams(gaslimit: int, amount: int):
    return Web3.to_hex(encode(["uint16", "uint64", "uint256"], [2, gaslimit, amount])[30:])

def check_merkly_fees():

    wallet = '0x7d4569a93937224bc4d6b679f25b899591efcccb' # рандомный кошелек

    result = {}

    for from_chain in MERKLY_CONTRACTS.items():
        from_chain = from_chain[0]

        result.update({from_chain:{}})

        web3 = Web3(Web3.HTTPProvider(DATA[from_chain]['rpc']))

        contract = web3.eth.contract(address=Web3.to_checksum_address(MERKLY_CONTRACTS[from_chain]), abi=ABI_MERKLY_REFUEL)
        adapterParams = get_adapterParams(250000, 1) + wallet[2:].lower()

        for to_chain in LAYERZERO_CHAINS_ID.items():
            to_chain = to_chain[0]

            if from_chain != to_chain:

                try:
                    send_value = contract.functions.estimateGasBridgeFee(LAYERZERO_CHAINS_ID[to_chain], False, adapterParams).call()
                    send_value = decimalToInt(send_value[0], 18)
                    send_value = round_to(send_value * PRICES_NATIVE[from_chain])
                    cprint(f'{from_chain} => {to_chain} : {send_value}', 'white')
                    result[from_chain].update({to_chain:send_value})
                except Exception as error:
                    cprint(f'{from_chain} => {to_chain} : None', 'white')
                    result[from_chain].update({to_chain:None})

    path = 'results/merkly_refuel'
    call_json(result, path)
    cprint(f'\nРезультаты записаны в {path}.json\n', 'blue')
    sys.exit()

class MerklyRefuel:
    
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
            self.from_chain = Value_Merkly_Refuel.from_chain
            self.to_chain = Value_Merkly_Refuel.to_chain
            self.amount_from = Value_Merkly_Refuel.amount_from
            self.amount_to = Value_Merkly_Refuel.amount_to
            self.swap_all_balance = Value_Merkly_Refuel.swap_all_balance
            self.min_amount_swap = Value_Merkly_Refuel.min_amount_swap
            self.keep_value_from = Value_Merkly_Refuel.keep_value_from
            self.keep_value_to = Value_Merkly_Refuel.keep_value_to
            self.get_layerzero_fee = Value_Merkly_Refuel.get_layerzero_fee
        self.key = key
        self.number = number

    async def setup(self):
        self.from_chain = random.choice(self.from_chain)
        self.to_chain = random.choice(self.to_chain)
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, '', self.amount_from, self.amount_to)
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.adapterParams = get_adapterParams(250000, self.value) + self.manager.address[2:].lower()
        self.module_str = f'{self.number} {self.manager.address} | merkly_refuel : {self.from_chain} => {self.to_chain}'

        if self.get_layerzero_fee:
            check_merkly_fees()

    async def get_txn(self):

        try:

            contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(MERKLY_CONTRACTS[self.from_chain]), abi=ABI_MERKLY_REFUEL)
            send_value = await contract.functions.estimateGasBridgeFee(LAYERZERO_CHAINS_ID[self.to_chain], False, self.adapterParams).call()

            contract_txn = await contract.functions.bridgeGas(
                    LAYERZERO_CHAINS_ID[self.to_chain],
                    '0x0000000000000000000000000000000000000000', # _zroPaymentAddress
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
