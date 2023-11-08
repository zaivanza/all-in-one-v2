from config import STR_CANCEL
from .utils.contracts.abi import ABI_ZKSYNC_BRIDGE
from .utils.helpers import round_to, list_send, intToDecimal
from .utils.manager_async import Web3ManagerAsync
from setting import Value_ZkSyncBridge

from loguru import logger
from web3 import Web3
import random

class ZkSyncBridge:
    
    def __init__(self, key, number, params=None):
        self.params = params
        self.from_chain = "ethereum"
        self.to_chain = "zksync"

        if self.params:
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.bridge_all_balance = self.params['bridge_all_balance']
            self.min_amount_bridge = self.params['min_amount_bridge']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
        else:
            self.amount_from = Value_ZkSyncBridge.amount_from
            self.amount_to = Value_ZkSyncBridge.amount_to
            self.bridge_all_balance = Value_ZkSyncBridge.bridge_all_balance
            self.min_amount_bridge = Value_ZkSyncBridge.min_amount_bridge
            self.keep_value_from = Value_ZkSyncBridge.keep_value_from
            self.keep_value_to = Value_ZkSyncBridge.keep_value_to

        self.key = key
        self.number = number

    async def setup(self):
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.bridge_all_balance, '', self.amount_from, self.amount_to)
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.module_str = f'{self.number} {self.manager.address} | zksync_bridge'
        self.contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address("0x32400084C286CF3E17e7B677ea9583e60a000324"), abi=ABI_ZKSYNC_BRIDGE)
        self.gas_limit = random.randint(700000, 1000000)

    async def get_tx_data(self, base_cost: int, value: int):
        contract_txn = await self.contract.functions.requestL2Transaction(
                self.manager.address, # _contractL2
                value, # _l2Value
                "0x", # _calldata
                self.gas_limit, # _l2GasLimit
                800, # _l2GasPerPubdataByteLimit
                [], # _factoryDeps
                self.manager.address # _refundRecipient
        ).build_transaction(
            {
                "from": self.manager.address,
                "value": value + base_cost,
                "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                "gasPrice": await self.manager.web3.eth.gas_price,
            }
        )
        return contract_txn

    async def get_txn(self):
        try:
            base_cost = await self.contract.functions.l2TransactionBaseCost(await self.manager.web3.eth.gas_price, self.gas_limit, 800).call()
            contract_txn = await self.get_tx_data(base_cost, 1)

            if self.bridge_all_balance:
                bridgeValue = int(self.value - contract_txn["gasPrice"]*contract_txn["gas"]*1.05 - base_cost)
            else:
                bridgeValue = self.value

            contract_txn = await self.get_tx_data(base_cost, bridgeValue)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.amount >= self.min_amount_bridge:
                return contract_txn
            else:
                logger.error(f"{self.module_str} | {self.amount} (amount) < {self.min_amount_bridge} (min_amount_bridge)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | {round_to(self.amount)} less {self.min_amount_bridge}')
                return False
            
        except Exception as error:
            logger.error(error)
            return False
