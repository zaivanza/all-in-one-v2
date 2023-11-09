from config import STR_CANCEL, STARKNET_WALLETS
from .utils.contracts.abi import ABI_STARKGATE
from .utils.helpers import round_to, list_send, intToDecimal
from .utils.manager_async import Web3ManagerAsync
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient
from datas.data import DATA
from setting import Value_Starkgate

from loguru import logger
from web3 import Web3

class Starkgate:
    
    def __init__(self, key, number, params=None):
        self.params = params
        self.from_chain = "ethereum"
        self.to_chain = "starknet"

        if self.params:
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.bridge_all_balance = self.params['bridge_all_balance']
            self.min_amount_bridge = self.params['min_amount_bridge']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']

        else:
            self.amount_from = Value_Starkgate.amount_from
            self.amount_to = Value_Starkgate.amount_to
            self.bridge_all_balance = Value_Starkgate.bridge_all_balance
            self.min_amount_bridge = Value_Starkgate.min_amount_bridge
            self.keep_value_from = Value_Starkgate.keep_value_from
            self.keep_value_to = Value_Starkgate.keep_value_to

        self.key = key
        self.number = number

        self.client = FullNodeClient(DATA["starknet"]["rpc"])
        try:
            self.starknet_address = STARKNET_WALLETS[self.key] 
        except:
            raise Exception("Put the starknet wallet addresses in data/starknet_address.txt")

    async def setup(self):
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.bridge_all_balance, '', self.amount_from, self.amount_to)
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address("0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"), abi=ABI_STARKGATE)
        self.module_str = f'{self.number} {self.manager.address} | starkgate_bridge'
    
    async def get_l2_gas(self, amount: int):
        estimate_fee = await self.client.estimate_message_fee(
            from_address="0xae0ee0a63a2ce6baeeffe56e7714fb4efe48d419",
            to_address="0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
            entry_point_selector=get_selector_from_name("handle_deposit"),
            payload=[
                self.manager.address,
                amount,
                0
            ]
        )
        return estimate_fee.overall_fee
    
    async def get_tx_data(self, gas_l2: int, value: int):
        contract_txn = await self.contract.functions.deposit(
                    value,
                    int(self.starknet_address, 16)
                ).build_transaction(
                {
                    "from": self.manager.address,
                    "value": value + gas_l2,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': await self.manager.web3.eth.gas_price,
                }
            )
        return contract_txn

    async def get_txn(self):

        try:
            gas_l2 = await self.get_l2_gas(self.value)
            contract_txn = await self.get_tx_data(gas_l2, 1)

            if self.bridge_all_balance:
                bridgeValue = int(self.value - contract_txn["gasPrice"]*contract_txn["gas"]*1.1 - gas_l2)
            else:
                bridgeValue = self.value

            contract_txn = await self.get_tx_data(gas_l2, bridgeValue)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.amount >= self.min_amount_bridge:
                return contract_txn
            else:
                logger.error(f"{self.module_str} | {self.amount} (amount) < {self.min_amount_bridge} (min_amount_bridge)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | {round_to(self.amount)} less {self.min_amount_bridge}')
                return False
            
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} | {error}')
            return False
