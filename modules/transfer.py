from config import RECIPIENTS_WALLETS, STR_CANCEL
from setting import Value_Transfer
from .utils.helpers import round_to, list_send, intToDecimal
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3
import random

class Transfer:
    
    def __init__(self, key, number, params=None):
        self.params = params
        if self.params:
            self.chain = self.params['chain']
            self.token_address = self.params['token_address']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.transfer_all_balance = self.params['transfer_all_balance']
            self.min_amount_transfer = self.params['min_amount_transfer']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
        else:
            self.chain = Value_Transfer.chain
            self.token_address = Value_Transfer.token_address
            self.amount_from = Value_Transfer.amount_from
            self.amount_to = Value_Transfer.amount_to
            self.transfer_all_balance = Value_Transfer.transfer_all_balance
            self.min_amount_transfer = Value_Transfer.min_amount_transfer
            self.keep_value_from = Value_Transfer.keep_value_from
            self.keep_value_to = Value_Transfer.keep_value_to
        self.key = key
        self.number = number

    async def setup(self):
        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.to_address = RECIPIENTS_WALLETS[self.key]
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.transfer_all_balance, self.token_address, self.amount_from, self.amount_to, 0.999)
        self.token_data = await self.manager.get_token_info(self.token_address)
        self.value = intToDecimal(self.amount, self.token_data['decimal']) 
        self.module_str = f'{self.number} {self.manager.address} | {round_to(self.amount)} {self.token_data["symbol"]} transfer => {self.to_address}'

    async def get_txn(self):

        try:

            if self.token_address == '':
                contract_txn = {
                    'from': self.manager.address,
                    'chainId': self.manager.chain_id,
                    'gasPrice': 0,
                    'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gas': 0,
                    'to': Web3.to_checksum_address(self.to_address),
                    'value': self.value
                }

            else:
                contract_txn = await self.token_data['contract'].functions.transfer(
                    Web3.to_checksum_address(self.to_address),
                    int(self.value)
                    ).build_transaction(
                        {
                            'from': self.manager.address,
                            'chainId': self.manager.chain_id,
                            'gasPrice': 0,
                            'gas': 0,
                            'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.address),
                            'value': 0
                        }
                    )
                
            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit(contract_txn)

            if (self.transfer_all_balance and self.token_address == ''):
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice']) # нужно добавить умножение на multiplier (1.1 например)
                contract_txn['value'] = contract_txn['value'] - gas_gas

            if not self.manager.get_total_fee(contract_txn):
                return False

            if self.amount >= self.min_amount_transfer:
                return contract_txn
            else:
                logger.error(f"{self.module_str} | amount < {self.min_amount_transfer} (min_amount_transfer)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | amount less {self.min_amount_transfer}')
                return False
            
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} | {error}')
            return False


