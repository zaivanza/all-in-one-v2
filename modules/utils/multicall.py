from loguru import logger
import eth_abi
from eth_utils import function_abi_to_4byte_selector

from web3._utils.abi import get_abi_output_types, map_abi_data
from web3._utils.normalizers import BASE_RETURN_NORMALIZERS

from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import asyncio, aiohttp

from .contracts.contract import MULTICALL_ETH_CONTRACTS, MULTICALL_CONTRACTS
from config import ERC20_ABI, MULTICALL_ABI
from datas.data import DATA
from .helpers import decimalToInt
import math

def get_abi(type_: str):
    for data in ERC20_ABI:
        if data["name"] == type_:
            return data

class Multicall():
	
    def __init__(self, chain):
        self.chain = chain
        self.web3 = Web3(AsyncHTTPProvider(DATA[self.chain]['rpc']), modules={"eth": AsyncEth}, middlewares=[])

    async def aggregate3(self, calls):

        try:

            contract = self.web3.eth.contract(address = MULTICALL_CONTRACTS[self.chain], abi = MULTICALL_ABI)
            call_result = await self.web3.eth.call({
                'to': MULTICALL_CONTRACTS[self.chain],
                'data': contract.encodeABI(fn_name = 'aggregate3', args = [calls])
            })

            aggregate3_abi = {"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"allowFailure","type":"bool"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call3[]","name":"calls","type":"tuple[]"}],"name":"aggregate3","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"}
            output_types = get_abi_output_types(aggregate3_abi)
            decoded = self.web3.codec.decode(output_types, call_result)
            return decoded[0]
    
        except Exception as error:
            logger.error(f'[{ self.chain}] calls : {calls} | error : {error}')

    async def get_token_symbols(self, token_list):

        abi = get_abi("symbol")
        output_types = get_abi_output_types(abi)

        calls = []
        for token_address in token_list:
            selector = function_abi_to_4byte_selector(abi)
            calldata = '0x' + selector.hex()
            calls.append({
                'target': Web3.to_checksum_address(token_address),
                'allowFailure': False,
                'callData': calldata
            })

        try:
            multicall_result = await self.aggregate3(calls)
            decimals_list = [self._normalize_output(output_types, byte_values) for (success, byte_values) in multicall_result]
            
            blank_list = [0] * len(token_list)
            decimals_dict = dict(zip(token_list, blank_list))
            for i, token_address in enumerate(token_list):
                decimals_dict.update({token_address: decimals_list[i]})

            return decimals_dict

        except Exception as e:
            logger.error(f"Multicall error : {e}")
            return {}

    async def get_token_decimals(self, token_list):

        abi = get_abi("decimals")
        output_types = get_abi_output_types(abi)

        list_calls = []
        for token_address in token_list:
            selector = function_abi_to_4byte_selector(abi)
            calldata = '0x' + selector.hex()
            list_calls.append({
                'target': Web3.to_checksum_address(token_address),
                'allowFailure': False,
                'callData': calldata
            })

        len_batch = 1000
        all_calls = [list_calls[i:i + len_batch] for i in range(0, len(list_calls), len_batch)] # делим запросы на части по 1000

        decimals_dict = {}
        for lens, calls in enumerate(all_calls, start=1):
            try:
                multicall_result = await self.aggregate3(calls)
                decimals_list = [self._normalize_output(output_types, byte_values) for (success, byte_values) in multicall_result]
                
                blank_list = [0] * len(token_list)
                decimals_dict.update(zip(token_list, blank_list))
                for i, token_address in enumerate(token_list):
                    decimals_dict.update({token_address: decimals_list[i]})

            except Exception as e:
                logger.error(f"Multicall error ({calls}) : {e}")
        
        return decimals_dict

    async def fetch_eth_balance(self, session, user_address, convert_from_wei=True):
        params = {
            'jsonrpc': '2.0',
            'method': 'eth_getBalance',
            'params': [user_address, 'latest'],
            'id': 1
        }
        
        async with session.post(DATA["zksync"]['rpc'], json=params) as response:
            while True:
                if response.status == 200:
                    result = await response.json()
                    if 'result' in result:
                        res = int(result['result'], 16)
                        if convert_from_wei:
                            return float(Web3.from_wei(res, 'ether'))
                        else:
                            return res
                    else:
                        logger.error(f'[{user_address}] Ошибка при получении баланса ETH')
                        return 0
                else:
                    logger.error(f'Multicall error: {response.status}')
                    await asyncio.sleep(1)

    async def get_eth_balance_zksync_lite_batch(self, wallets, convert_from_wei=True):
        '''doesnt work'''
        
        len_batch = 50
        wallets_list = [wallets[i:i + len_batch] for i in range(0, len(wallets), len_batch)]

        balance_dict = {}
        async with aiohttp.ClientSession() as session:
            for i, wallets_batch in enumerate(wallets_list):
                tasks = [self.fetch_eth_balance(session, user_address, convert_from_wei) for user_address in wallets_batch]
                results = await asyncio.gather(*tasks)
                
                for user_address, result in zip(wallets_batch, results):
                    user_address = user_address.lower()
                    balance_dict[user_address] = result
        
        return balance_dict

    async def get_eth_balances(self, wallets, convert_from_wei = True):
        token_address = "0x0000000000000000000000000000000000000000"
        wallets_ = [Web3.to_checksum_address(wallet) for wallet in wallets]

        try:

            len_batch = 1000
            wallets_batches = [wallets_[i:i + len_batch] for i in range(0, len(wallets_), len_batch)]

            balances = {}
            for lens, wallets_list in enumerate(wallets_batches, start=1):

                abi = '[{"constant":true,"inputs":[{"name":"user","type":"address"},{"name":"token","type":"address"}],"name":"tokenBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"users","type":"address[]"},{"name":"tokens","type":"address[]"}],"name":"balances","outputs":[{"name":"","type":"uint256[]"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"}]'
                multicall_contract = self.web3.eth.contract(address=Web3.to_checksum_address(MULTICALL_ETH_CONTRACTS[self.chain]), abi=abi)
                multicall_result = await multicall_contract.functions.balances(
                    wallets_list, [token_address]
                ).call()

                logger.info(f'eth {lens * len(wallets_list)} / {len(wallets_)} calls [{self.chain}]')
                
                for i, balance in enumerate(multicall_result):
                    if convert_from_wei:
                        balance = decimalToInt(balance, 18)
                    balances[wallets_list[i].lower()] = balance

            return balances
        
        except Exception as e:
            logger.error(f"Multicall error : {e}")
            return {}

    async def get_balances(self, wallets, tokens_list, symbols_list, decimals_list):

        if "" in tokens_list:
            index = tokens_list.index("")  # Находим индекс первого вхождения элемента
            tokens_list[index] = "0x0000000000000000000000000000000000000000" 
            
        wallets_ = [Web3.to_checksum_address(wallet) for wallet in wallets]
        tokens_list = [Web3.to_checksum_address(token) for token in tokens_list]

        batch_limit = 1000
        len_batch = math.floor(batch_limit / len(tokens_list))
        wallets_batches = [wallets_[i:i + len_batch] for i in range(0, len(wallets_), len_batch)]           

        balances_dict = {}
        zero = 0
        for wallets_list in wallets_batches:
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    abi = '[{"constant":true,"inputs":[{"name":"user","type":"address"},{"name":"token","type":"address"}],"name":"tokenBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"users","type":"address[]"},{"name":"tokens","type":"address[]"}],"name":"balances","outputs":[{"name":"","type":"uint256[]"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"}]'
                    multicall_contract = self.web3.eth.contract(address=Web3.to_checksum_address(MULTICALL_ETH_CONTRACTS[self.chain]), abi=abi)
                    multicall_result = await multicall_contract.functions.balances(
                        wallets_list, tokens_list
                    ).call()

                    zero += len(wallets_list)
                    logger.info(f'{zero} / {len(wallets_)} wallets [{self.chain}]')
                    multicall_result = [multicall_result[i:i + len(tokens_list)] for i in range(0, len(multicall_result), len(tokens_list))]     

                    for number, wallet in enumerate(wallets_list):
                        balances = multicall_result[number]
                        balances_dict[wallet] = {}
                    
                        for i, balance in enumerate(balances):
                            token = tokens_list[i]
                            if token == '0x0000000000000000000000000000000000000000':
                                symbol = DATA[self.chain]['token']
                                decimal = 18
                            else:
                                symbol  = symbols_list[self.chain][token]
                                decimal = decimals_list[self.chain][token]
                            balances_dict[wallet][symbol] = decimalToInt(balance, decimal)
                    break
                
                except Exception as e:
                    logger.info(f'[{self.chain}] Multicall error : {e} | attempt {attempt+1}/{max_attempts}')
                    await asyncio.sleep(1)

        return balances_dict
    
    async def get_erc20_balances(self, wallets, token_list, symbols_list, decimals_list, convert_from_wei = True):

        abi = get_abi("balanceOf")
        output_types = get_abi_output_types(abi)

        balance_dict = {}

        logger.info('collecting calls...')
        list_calls = []
        for i, user_address in enumerate(wallets, start=1):
            print(f'\r{i} / {len(wallets)}', end='', flush=True)
            for token_address in token_list:
                token_contract = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
                list_calls.append({
                    'target': Web3.to_checksum_address(token_address),
                    'allowFailure': False,
                    'callData': token_contract.encodeABI(fn_name='balanceOf', args=[Web3.to_checksum_address(user_address)])
                })
        print()

        len_batch = 500
        all_calls = [list_calls[i:i + len_batch] for i in range(0, len(list_calls), len_batch)] # делим запросы на части по 1000

        all_balances = []
        for lens, calls in enumerate(all_calls, start=1):

            multicall_result = await self.aggregate3(calls)
            balance_list = [self._normalize_output(output_types, byte_values) for (success, byte_values) in multicall_result]
            all_balances += balance_list
            logger.info(f'erc20 {lens * len(calls)} / {len(list_calls)} calls [{self.chain}]')
                
        for i, user_address in enumerate(wallets):
            user_address = user_address.lower()
            balance_dict[user_address] = {}
            for j, token_address in enumerate(token_list):
                symbol = symbols_list[self.chain][token_address]
                decimals = decimals_list[self.chain][token_address] if convert_from_wei else 0
                balance = all_balances[i * len(token_list) + j] / 10 ** decimals
                balance_dict[user_address].update({symbol: balance})
        
        return balance_dict

    async def get_nft_balances(self, wallets, nft_address):

        abi = get_abi("balanceOf")
        output_types = get_abi_output_types(abi)

        len_batch = 1000
        wallets_batches = [wallets[i:i + len_batch] for i in range(0, len(wallets), len_batch)]

        balance_dict = {}
        for wallets in wallets_batches:
            calls = []
            for user_address in wallets:
                token_contract = self.web3.eth.contract(address=Web3.to_checksum_address(nft_address), abi=ERC20_ABI)
                calls.append({
                    'target': Web3.to_checksum_address(nft_address),
                    'allowFailure': False,
                    'callData': token_contract.encodeABI(fn_name='balanceOf', args=[Web3.to_checksum_address(user_address)])
                })

            try:
                multicall_result = await self.aggregate3(calls)
                balance_list = [self._normalize_output(output_types, byte_values) for (success, byte_values) in multicall_result]
                for i, wallet in enumerate(wallets):
                    balance_dict[wallet] = balance_list[i]

            except Exception as e:
                logger.error(f"Multicall error : {e}")
        return balance_dict

    async def get_allowances(self, wallets, spender_list, token_list, convert_from_wei = True):

        abi = get_abi("allowance")
        output_types = get_abi_output_types(abi)

        calls = []
        for user_address in wallets:
            for spender_address in spender_list:
                for token_address in token_list:
                    selector = function_abi_to_4byte_selector(abi)
                    arguments = eth_abi.encode(
                        ['address', 'address'], 
                        [Web3.to_checksum_address(user_address), Web3.to_checksum_address(spender_address)]
                    )
                    calldata = '0x' + selector.hex() + arguments.hex()
                    calls.append({
                        'target': Web3.to_checksum_address(token_address),
                        'allowFailure': False,
                        'callData': calldata
                    })

        try:
            if convert_from_wei:
                decimals_dict = await self.get_token_decimals(token_list)

            multicall_result = await self.aggregate3(calls)
            allowance_list = [self._normalize_output(output_types, byte_values) for (success, byte_values) in multicall_result]
            
            blank_list = [0] * len(token_list)
            allowance_dict = {}
            for i, user_address in enumerate(wallets):
                allowance_dict[user_address] = {}
                for j, spender_address in enumerate(spender_list): 
                    allowance_dict[user_address][spender_address] = dict(zip(token_list, blank_list))
                    for k, token_address in enumerate(token_list):
                        decimals = decimals_dict[token_address] if convert_from_wei else 0
                        index = i * len(spender_list) * len (token_list) + j * len(token_list) + k
                        allowance = allowance_list[index] / 10 ** decimals
                        allowance_dict[user_address][spender_address].update({token_address: allowance})

            return allowance_dict

        except Exception as e:
            logger.error(f"Multicall error in get_allowances() | {e}")
            return {}

    def _normalize_output(self, output_types, byte_values):
        output_decoded = eth_abi.decode(output_types, byte_values)
        output_normalized = map_abi_data(BASE_RETURN_NORMALIZERS, output_types, output_decoded)
        return output_normalized[0] if len(output_normalized) == 1 else output_normalized
          


