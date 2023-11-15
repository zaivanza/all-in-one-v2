import asyncio
import aiohttp
import asyncio
from loguru import logger
import random
from config import PROXIES
from modules.utils.helpers import decimalToInt

def split_dict(input_dict, chunk_size):
    iter_items = iter(input_dict.items())
    result = []
    for first in iter_items:
        chunk = dict([first] + [next(iter_items, (None, None)) for _ in range(chunk_size - 1) if first[0] is not None])
        if bool(chunk): # make sure it's not an empty dictionary
            result.append(chunk)

    return result

class Starknet:

    def get_token_decimals(self, token_contract: str) -> int:
        decimals = {
            '0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8' : 6,   # USDC
            '0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8' : 6,   # USDT
            '0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3' : 18,  # DAI
            '0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac' : 8,   # WBTC
            '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7' : 18,  # ETH
        }
        return decimals[token_contract.lower()]

    def get_token_address(self, token_symbol: str) -> str:
        contracts = {
            'USDC' : '0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8',
            'USDT' : '0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8',
            'DAI'  : '0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3',
            'WBTC' : '0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac',
            'ETH'  : '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7'
        }
        return contracts[token_symbol]

    async def get_balance(self, token_symbol: str, wallet: str) -> dict:
        token_contract = self.get_token_address(token_symbol)
        token_decimals = self.get_token_decimals(token_contract)
        json_data = {
            'signature': [],
            'contract_address': token_contract.lower(),
            'entry_point_selector': '0x2e4263afad30923c891518314c3c95dbe830a16874e8abc5777a9a20b54c76e',
            'calldata': [wallet],
        }
        async with aiohttp.ClientSession() as session:
            attempt = 1
            max_attempt = 5
            timeout = 5 # Set your desired maximum wait time in seconds
            while attempt <= max_attempt:  
                try:
                    request_kwargs = {
                        'url': 'https://alpha-mainnet.starknet.io/feeder_gateway/call_contract',
                        'params': {'blockNumber': 'pending'},
                        'json': json_data,
                        'timeout': timeout
                    }
                    if PROXIES:
                        request_kwargs['proxy'] = random.choice(PROXIES)
                        
                    async with session.post(**request_kwargs) as response:
                        if response.status == 200: 
                            response_json = await response.json()
                            balance = int(response_json['result'][0], 0)
                            self.balances[wallet][token_symbol] = decimalToInt(balance, token_decimals)
                            break
                        if response.status == 429:
                            logger.info(f'429 Too Many Requests. Sleeping 10 sec | {attempt}/{max_attempt}')
                            await asyncio.sleep(10)  # Sleep for a bit before retrying
                        else:
                            logger.info(f'{response.status}. Try to get balance again: {attempt}/{max_attempt}')
                            await asyncio.sleep(1) 

                # except asyncio.TimeoutError:
                #     logger.info(f'Request timed out: {attempt}/{max_attempt}')

                except Exception as e:
                    pass
                    # logger.info(f"An error occurred: {e}. {attempt}/{max_attempt}")

                if attempt <= max_attempt:
                    await asyncio.sleep(1)  # Sleep for a bit before retrying
                else:
                    logger.error(f'Couldnt get a balance [{wallet}]')
                attempt += 1

    async def main_balances(self, wallets_list: list, tokens: list):
        logger.info('getting balances...')
        wallets = [wallet.lower() for wallet in wallets_list]
        self.balances = {wallet: {token: 0 for token in tokens} for wallet in wallets}

        batch_limit = 50
        wallets_keys = list(self.balances.keys())
        batches = [wallets_keys[i:i + batch_limit] for i in range(0, len(wallets_keys), batch_limit)]

        zero = 0
        for batch in batches:
            current_batch_dict = {wallet: self.balances[wallet] for wallet in batch}
            zero += len(current_batch_dict)
            tasks = []
            for wallet, tokens in current_batch_dict.items():
                for token in tokens:
                    tasks.append(asyncio.create_task(self.get_balance(token, wallet)))
            await asyncio.gather(*tasks)
            logger.info(f'{zero}/{len(self.balances)}')
        return self.balances
