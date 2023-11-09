from datas.data import API_0x
from setting import Value_0x_Swap
from config import  STR_CANCEL
from .utils.helpers import round_to, list_send, intToDecimal
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3
import aiohttp, asyncio
import random

class ZeroXswap:

    def __init__(self, key, number, params=None):
        self.params = params
        if self.params:
            self.chain = self.params['chain']
            self.from_token_address = self.params['from_token_address']
            self.to_token_address = self.params['to_token_address']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.swap_all_balance = self.params['swap_all_balance']
            self.min_amount_swap = self.params['min_amount_swap']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
            self.slippage = self.params['slippage']
        else:
            self.chain = Value_0x_Swap.chain
            self.from_token_address = Value_0x_Swap.from_token_address
            self.to_token_address = Value_0x_Swap.to_token_address
            self.amount_from = Value_0x_Swap.amount_from
            self.amount_to = Value_0x_Swap.amount_to
            self.swap_all_balance = Value_0x_Swap.swap_all_balance
            self.min_amount_swap = Value_0x_Swap.min_amount_swap
            self.keep_value_from = Value_0x_Swap.keep_value_from
            self.keep_value_to = Value_0x_Swap.keep_value_to
            self.slippage = Value_0x_Swap.slippage
        self.key = key
        self.number = number

    async def setup(self):
        self.from_token_address = random.choice(self.from_token_address)
        self.to_token_address = random.choice(self.to_token_address)
        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.address = self.manager.address
        self.from_token_data = await self.manager.get_token_info(self.from_token_address)
        self.to_token_data = await self.manager.get_token_info(self.to_token_address)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, self.from_token_address, self.amount_from, self.amount_to, 0.999)
        self.value = intToDecimal(self.amount, self.from_token_data['decimal']) 
        self.module_str = f'{self.number} {self.manager.address} | 0x_swap ({self.chain}) : {round_to(self.amount)} {self.from_token_data["symbol"]} => {self.to_token_data["symbol"]}'

    async def get_0x_quote(self):
        from_token = self.from_token_data['address']
        to_token = self.to_token_data['address']

        url_chains = {
            'ethereum'  : '',
            'bsc'       : 'bsc.',
            'arbitrum'  : 'arbitrum.',
            'optimism'  : 'optimism.',
            'polygon'   : 'polygon.',
            'fantom'    : 'fantom.',
            'avalanche' : 'avalanche.',
            'celo'      : 'celo.',
        }

        url = f'https://{url_chains[self.chain]}api.0x.org/swap/v1/quote?buyToken={to_token}&sellToken={from_token}&sellAmount={self.value}&slippagePercentage={self.slippage/100}'
        headers = {'0x-api-key' : API_0x}

        try:
            max_attempts = 10 # Максимальное количество попыток

            for attempt in range(max_attempts):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result
                        logger.info(f'attempt to get a response {attempt+1}/{max_attempts}')
                        await asyncio.sleep(1)
            logger.error("couldn't get a response")
            return False # Если не удалось получить response после max_attempts попыток
    
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return False

    async def get_txn(self):

        try:

            json_data = await self.get_0x_quote()
            if json_data is False: return False

            spender = json_data['allowanceTarget']
            # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апрув
            if self.from_token_address != '':
                await self.manager.approve(self.value, self.from_token_address, spender)

            contract_txn = {
                'from'      : self.address,
                'chainId'   : self.manager.chain_id,
                'gasPrice'  : int(json_data['gasPrice']),
                'nonce'     : await self.manager.web3.eth.get_transaction_count(self.address),
                'gas'       : int(json_data['gas']),
                'to'        : Web3.to_checksum_address(json_data['to']),
                'data'      : json_data['data'],
                'value'     : int(json_data['value']),
            }

            contract_txn['gas'] = int(contract_txn['gas'] * 1.5)

            if (self.from_token_address == '' and self.swap_all_balance):
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
            
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} | {error}')
            return False

