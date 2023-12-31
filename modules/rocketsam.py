from config import STR_CANCEL, STR_DONE
from .utils.contracts.abi import ABI_ROCKETSAM
from .utils.contracts.contract import ROCKETSAM_CONTRACTS
from .utils.helpers import list_send, intToDecimal, async_sleeping, decimalToInt, round_to
from .utils.manager_async import Web3ManagerAsync
from setting import Value_RocketSam, RETRY, IS_SLEEP, DELAY_SLEEP
from datas.data import DATA

from loguru import logger
from web3 import Web3
import random
import asyncio

class RocketSam:

    GAS_MULTIPLIER = 3  # Multiplier for gas to ensure sufficient for withdrawal
    
    def __init__(self, key: str, number: str):
        self.key = key
        self.number = number
        self.chain = random.choice(Value_RocketSam.chain)
        self.amount_interactions = random.randint(*Value_RocketSam.amount_interactions)
        self.deposit_all_balance = Value_RocketSam.deposit_all_balance
        self.deposit_value = Value_RocketSam.deposit_value
        self.module = Value_RocketSam.module
        self.keep_values = Value_RocketSam.keep_values

    async def setup(self):
        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.amount = await self.manager.get_amount_in(
            self.keep_values[0], self.keep_values[1], self.deposit_all_balance, '', self.deposit_value[0], self.deposit_value[1]
        )
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.module_str = f'{self.number} {self.manager.address} | rocketsam'

    async def get_contract(self, contract_address: str):
        return self.manager.web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=ABI_ROCKETSAM)

    async def get_contract_with_least_number_txs(self):
        logger.info('Searching for the pool with the least number of interactions')
        pools = {}
        for contract_address in ROCKETSAM_CONTRACTS[self.chain]:
            depositsCount, depositsVolume = await self.get_address_pool_statistic(contract_address)
            pools[contract_address] = depositsCount
        return min(pools, key=pools.get)
    
    async def get_deposit_fee(self, contract_address: str, value: int):
        contract = await self.get_contract(contract_address)
        fee = await contract.functions.estimateProtocolFee(value).call()
        return fee

    async def get_address_pool_statistic(self, contract_address: str):
        contract = await self.get_contract(contract_address)
        statistic = await contract.functions.addressStatistic(self.manager.address).call()
        depositsCount = statistic[0]
        depositsVolume = statistic[1]
        return depositsCount, depositsVolume
    
    async def get_contract_pools_with_balance(self):
        pools = []
        for contract_address in ROCKETSAM_CONTRACTS[self.chain]:
            contract = await self.get_contract(contract_address)
            balance = await contract.functions.balances(self.manager.address).call()
            if balance > 0:
                pools.append(contract_address)
        return pools

    async def get_deposit_txn(self, module: int):
        try:
            contract_address = await self.get_contract_with_least_number_txs()
            contract = await self.get_contract(contract_address)
            fee = await self.get_deposit_fee(contract_address, self.value)

            # pass value 1 for gas counting
            contract_txn = await contract.functions.deposit(1).build_transaction(
                {
                    "from": self.manager.address,
                    "value": 1 + fee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': await self.manager.web3.eth.gas_price,
                }
            )

            contract_txn["gas"] = int(contract_txn["gas"] * 1.2)

            if self.deposit_all_balance:
                if module   == 1: multiplier = 1
                elif module == 2: multiplier = self.GAS_MULTIPLIER 
                amount = int((self.value - fee - (contract_txn["gas"] * contract_txn["gasPrice"] * multiplier) * 0.9999) - round(random.uniform(*self.keep_values), 8))
                value = int(amount + fee)
            else:
                amount = self.value
                value = int(amount + fee)

            if amount < 0:
                logger.error(f'{self.module_str} | amount < 0')
                return False, contract_address
            
            contract_txn = await contract.functions.deposit(amount).build_transaction(
                {
                    "from": self.manager.address,
                    "value": value,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': await self.manager.web3.eth.gas_price,
                    "gas": contract_txn["gas"]
                }
            )

            if self.manager.get_total_fee(contract_txn) == False: 
                return False, contract_address

            return contract_txn, contract_address

        except Exception as error:
            logger.error(f'{self.module_str} | {error}')
            # list_send.append(f'{STR_CANCEL}{self.module_str} | deposit | {error}')
            return False, contract_address
        
    async def get_withdraw_txn(self, contract_address: str, plus_nonce=0):
        try:
            contract = await self.get_contract(contract_address)
            contract_txn = await contract.functions.withdraw().build_transaction(
                {
                    "from": self.manager.address,
                    "value": 0,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address) + plus_nonce,
                    'gasPrice': await self.manager.web3.eth.gas_price,
                }
            )

            if self.manager.get_total_fee(contract_txn) == False: return False
            return contract_txn

        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} | withdraw | {error}')
            return False
        
    async def perform_transactions(self):
        txns = []
        if self.module == 1:
            contract_txn, _ = await self.get_deposit_txn(self.module)
            if contract_txn:
                txns.append(("deposit", contract_txn))

        elif self.module == 2:
            deposit_contract_txn, contract_address = await self.get_deposit_txn(self.module)
            if deposit_contract_txn:
                txns.append(("deposit", deposit_contract_txn))
                txns.append(("prepare_withdraw", contract_address))

        elif self.module == 3:
            pools_with_balance = await self.get_contract_pools_with_balance()
            for i, contract_address in enumerate(pools_with_balance):
                contract_txn = await self.get_withdraw_txn(contract_address, plus_nonce=i)
                if contract_txn:
                    txns.append(("withdraw", contract_txn))
        
        return txns
    
    async def send_transaction_with_retry(self, txn_type: str, txn_data):
        attempts = 0
        while attempts <= RETRY:
            if not txn_data:
                logger.error(f'{self.module_str} | {txn_type} | error getting contract_txn')
                attempts += 1
                continue
        
            if txn_type == "deposit" or txn_type == "withdraw":
                status, tx_link = await self.manager.send_tx(txn_data)
            elif txn_type == "prepare_withdraw":
                txn_data = await self.get_withdraw_txn(txn_data)
                status, tx_link = await self.manager.send_tx(txn_data)
                txn_type = "withdraw"

            if status == 1:
                if txn_type == "deposit":
                    logger.success(f'{self.module_str} | {txn_type} {round_to(decimalToInt(txn_data["value"], 18))} {DATA[self.chain]["token"]} | {tx_link}')
                else:
                    logger.success(f'{self.module_str} | {txn_type} | {tx_link}')
                return True
            elif status == 0:
                logger.error(f'{self.module_str} | {txn_type} | tx is failed | {tx_link}')
            else:
                logger.error(f'{self.module_str} | {txn_type} | {tx_link}')

            attempts += 1
            await asyncio.sleep(5) 

        return False
    
    async def main(self):
        for interaction in range(self.amount_interactions):
            await self.setup()
            txns = await self.perform_transactions()
            for txn_type, txn_data in txns:
                success = await self.send_transaction_with_retry(txn_type, txn_data)
                if txn_type == "prepare_withdraw":
                    txn_type = "withdraw"

                if success:
                    list_send.append(f'{STR_DONE}{self.module_str} | {txn_type}')
                else:
                    list_send.append(f'{STR_CANCEL}{self.module_str} | {txn_type}')

                if IS_SLEEP:
                    await async_sleeping(*DELAY_SLEEP)


