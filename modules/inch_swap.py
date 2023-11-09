from setting import Value_1inch_Swap
from config import STR_CANCEL
from .utils.helpers import list_send, intToDecimal, round_to
from .utils.manager_async import Web3ManagerAsync
from datas.data import API_1inch

from loguru import logger
from web3 import Web3
import random
import asyncio, aiohttp

class InchSwap:
        
    def __init__(self, key, number, params=None):
        self.key = key
        self.number = number
        self.params = params
        if self.params:
            self.chain = self.params['chain']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
            self.swap_all_balance = self.params['swap_all_balance']
            self.from_token_address = self.params['from_token_address']
            self.to_token_address = self.params['to_token_address']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.min_amount_swap = self.params['min_amount_swap']
            self.slippage = self.params['slippage']
        else:
            self.chain = Value_1inch_Swap.chain
            self.keep_value_from = Value_1inch_Swap.keep_value_from
            self.keep_value_to = Value_1inch_Swap.keep_value_to
            self.swap_all_balance = Value_1inch_Swap.swap_all_balance
            self.from_token_address = Value_1inch_Swap.from_token_address
            self.to_token_address = Value_1inch_Swap.to_token_address
            self.amount_from = Value_1inch_Swap.amount_from
            self.amount_to = Value_1inch_Swap.amount_to
            self.min_amount_swap = Value_1inch_Swap.min_amount_swap
            self.slippage = Value_1inch_Swap.slippage

    async def setup(self):
        self.from_token_address = random.choice(self.from_token_address)
        self.to_token_address = random.choice(self.to_token_address)
        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.from_token_data = await self.manager.get_token_info(self.from_token_address)
        self.to_token_data = await self.manager.get_token_info(self.to_token_address)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, self.from_token_address, self.amount_from, self.amount_to, 0.999)
        self.value = intToDecimal(self.amount, self.from_token_data['decimal']) 
        self.module_str = f'{self.number} {self.manager.address} | 1inch_swap ({self.chain}) : {round_to(self.amount)} {self.from_token_data["symbol"]} => {self.to_token_data["symbol"]}'
        self.base_url = 'https://api.1inch.dev/swap' # 'https://api-defillama.1inch.io'
        self.inch_version = 5.2

    async def get_api_call_data(self, url):
        max_attempts = 10 # Максимальное количество попыток

        for attempt in range(max_attempts):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'Authorization': API_1inch}) as response:
                    if response.status == 200:
                        return await response.json()

            logger.info(f'attempt to get a response {attempt+1}/{max_attempts}')
            await asyncio.sleep(1)

        logger.error("couldn't get a response")
        return False # Если не удалось получить response после max_attempts попыток

    async def get_txn(self):

        spender_json = await self.get_api_call_data(f'{self.base_url}/v{self.inch_version}/{self.manager.chain_id}/approve/spender')
        spender      = Web3.to_checksum_address(spender_json['address'])
        await asyncio.sleep(1.5) # rate limite : 1 req/s

        if self.from_token_address != '':
            await self.manager.approve(self.value, self.from_token_address, spender)

        _1inchurl = f"{self.base_url}/v{self.inch_version}/{self.manager.chain_id}/swap?fromTokenAddress={self.from_token_data['address']}&toTokenAddress={self.to_token_data['address']}&amount={self.value}&fromAddress={self.manager.address}&slippage={self.slippage}"
        json_data = await self.get_api_call_data(_1inchurl)
        if json_data is False: return False

        contract_txn  = json_data['tx']
        contract_txn['from']      = Web3.to_checksum_address(contract_txn['from'])
        contract_txn['chainId']   = self.manager.chain_id
        contract_txn['nonce']     = await self.manager.web3.eth.get_transaction_count(self.manager.address)
        contract_txn['to']        = Web3.to_checksum_address(contract_txn['to'])
        contract_txn['gasPrice']  = int(contract_txn['gasPrice'])
        contract_txn['gas']       = int(contract_txn['gas'])
        contract_txn['value']     = int(contract_txn['value'])

        contract_txn = await self.manager.add_gas_price(contract_txn)

        if (self.from_token_address == '' and self.swap_all_balance == True):
            gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
            contract_txn['value'] = int(int(self.value - gas_gas) * 0.999)

        is_fee = self.manager.get_total_fee(contract_txn)
        if is_fee is False: return False

        if self.amount >= self.min_amount_swap:
            return contract_txn
        else:
            logger.error(f"{self.module_str} | amount < {self.min_amount_swap} (min_amount_swap)")
            list_send.append(f'{STR_CANCEL}{self.module_str} | amount less {self.min_amount_swap}')
            return False


