from datas.data import DATA
from .utils.contracts.abi import ABI_BUNGEE_REFUEL
from .utils.contracts.contract import BUNGEE_REFUEL_CONTRACTS
from config import STR_CANCEL, BUNGEE_LIMITS
from setting import Value_Bungee
from .utils.helpers import round_to, list_send, decimalToInt, intToDecimal
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3
import random

class BungeeRefuel:
    
    def __init__(self, key, number, params=None):
        self.params = params
        if self.params:
            self.from_chain = self.params['from_chain']
            self.to_chain = self.params['to_chain']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.bridge_all_balance = self.params['bridge_all_balance']
            self.min_amount_bridge = self.params['min_amount_bridge']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
        else:
            self.from_chain = Value_Bungee.from_chain
            self.to_chain = Value_Bungee.to_chain
            self.amount_from = Value_Bungee.amount_from
            self.amount_to = Value_Bungee.amount_to
            self.bridge_all_balance = Value_Bungee.bridge_all_balance
            self.min_amount_bridge = Value_Bungee.min_amount_bridge
            self.keep_value_from = Value_Bungee.keep_value_from
            self.keep_value_to = Value_Bungee.keep_value_to
        self.key = key
        self.number = number

    async def setup(self):
        self.from_chain = random.choice(self.from_chain)
        self.to_chain = random.choice(self.to_chain)
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.bridge_all_balance, '', self.amount_from, self.amount_to)
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.module_str = f'{self.number} {self.manager.address} | bungee_refuel : {round_to(self.amount)} {self.token_data["symbol"]} {self.from_chain} => {self.to_chain}'

    def get_bungee_limits(self):

        from_chain_id   = DATA[self.from_chain]['chain_id']
        to_chain_id     = DATA[self.to_chain]['chain_id']

        data = BUNGEE_LIMITS

        for i in range(len(data['result'])):
            if data['result'][i]['chainId'] == from_chain_id:
                infos = data['result'][i]['limits']
                
                try:

                    if  [x for x in infos if x['chainId'] == to_chain_id][0] \
                    and [x for x in infos if x['chainId'] == to_chain_id][0]['isEnabled'] == True:
                        
                        info = [x for x in infos if x['chainId'] == to_chain_id][0]
                        return int(info['minAmount']), int(info['maxAmount'])
                    else:
                        logger.error(f'рефуел из {self.from_chain} в {self.to_chain} невозможен')
                        return 0, 0

                except Exception as error:
                    logger.error(error)

    async def get_txn(self):
        try:
            limits      = self.get_bungee_limits()
            min_limit   = round_to(decimalToInt(limits[0], 18))
            max_limit   = round_to(decimalToInt(limits[1], 18))
            if min_limit < self.amount < max_limit: None
            else: 
                logger.error(f'amount {self.amount} but bungee_limits : {min_limit} - {max_limit}')
                list_send.append(f'{STR_CANCEL}{self.module_str} | amount {self.amount} but bungee_limits : {min_limit} - {max_limit}')
                return False

            contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(BUNGEE_REFUEL_CONTRACTS[self.from_chain]), abi=ABI_BUNGEE_REFUEL)

            contract_txn = await contract.functions.depositNativeToken(
                DATA[self.to_chain]['chain_id'], # destinationChainId
                self.manager.address # _to
                ).build_transaction(
                {
                    "chainId": self.manager.chain_id,
                    "from": self.manager.address,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    "value": self.value,
                    "gas": 0,
                    "gasPrice": 0
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit(contract_txn)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.bridge_all_balance:
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = contract_txn['value'] - gas_gas

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

