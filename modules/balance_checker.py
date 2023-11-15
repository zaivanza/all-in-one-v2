from datas.data import DATA
from config import WALLETS, ERC20_ABI, STARKNET_ADDRESS
from setting import Value_EVM_Balance_Checker, Value_Starknet_Balance_Checker
from .utils.helpers import round_to
from .utils.multicall import Multicall
from .utils.starknet import Starknet

from loguru import logger
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import asyncio, aiohttp
from termcolor import cprint
import csv
from tabulate import tabulate

class EvmBalanceChecker:

    def __init__(self) -> None:
        self.file_name = 'balances'

    def get_web3(self, chain):
        return Web3(AsyncHTTPProvider(DATA[chain]['rpc']), modules={"eth": (AsyncEth)}, middlewares=[])

    async def get_tokens_data(self):
        logger.info('getting tokens data...')
        list_decimals = {}
        list_symbols = {}
        for chain, coins in Value_EVM_Balance_Checker.evm_tokens.items():
            web3 = self.get_web3(chain)
            list_decimals[chain] = {}
            list_symbols[chain] = {}
            for coin in coins:
                if coin != '':
                    coin = Web3.to_checksum_address(coin)
                    token_contract = web3.eth.contract(address=coin, abi=ERC20_ABI)
                    decimals = await token_contract.functions.decimals().call()
                    symbol = await token_contract.functions.symbol().call()
                    list_decimals[chain][coin] = decimals 
                    list_symbols[chain][coin] = symbol 

        logger.success('got tokens data')
        return list_decimals, list_symbols

    async def fetch_price(self, session, symbol, url):
        try:
            async with session.get(url) as response:
                result = await response.json()
                price = result['USDT']
                self.prices[symbol] = float(price)
        except Exception as error:
            logger.error(f'{symbol}: error. Set price: 0')
            self.prices[symbol] = 0

    async def get_prices(self):
        logger.info('getting prices...')
        self.prices = {}
        for chain, coins in Value_EVM_Balance_Checker.evm_tokens.items():
            web3 = self.get_web3(chain)
            for address_contract in coins:
                if address_contract == '':  # eth
                    symbol = DATA[chain]['token']
                else:
                    token_contract = web3.eth.contract(address=Web3.to_checksum_address(address_contract), abi=ERC20_ABI)
                    symbol = await token_contract.functions.symbol().call()

                self.prices.update({symbol: 0})

        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in self.prices:
                if symbol == 'CORE':
                    url = f'https://min-api.cryptocompare.com/data/price?fsym=COREDAO&tsyms=USDT'
                else:
                    url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
                
                tasks.append(self.fetch_price(session, symbol, url))

            await asyncio.gather(*tasks)

        logger.success('got prices')

    def combine_tokens_data(self, eth_coins: dict, erc20_balances: dict):
        result = {}
        
        for chain, data in eth_coins.items():
            if data:
                for wallet, eth_balance in data.items():
                    wallet = wallet.lower()
                    if wallet not in result:
                        result[wallet] = {}
                    result[wallet][chain] = {DATA[chain]["token"]: eth_balance}
            else:
                logger.error(f'{chain} : {data}')
        
        for chain, balances in erc20_balances.items():
            if balances:
                for wallet, tokens in balances.items():
                    wallet = wallet.lower()
                    if wallet not in result:
                        result[wallet] = {}
                    if chain not in result[wallet]:
                        result[wallet][chain] = {}
                    for token, balance in tokens.items():
                        result[wallet][chain][token] = balance
            else:
                logger.error(f'{chain} : {data}')
        
        return result

    def transform_dict(self, input_dict):
        result = {}
        for chain, wallets in input_dict.items():
            for wallet, tokens in wallets.items():
                if wallet not in result:
                    result[wallet] = {}
                result[wallet][chain] = tokens
        
        return result

    async def evm_balances(self):
        erc20_coins = {chain: [] for chain in Value_EVM_Balance_Checker.evm_tokens}
        decimals_list, symbols_list = await self.get_tokens_data()
        tasks = [Multicall(chain).get_balances(WALLETS, tokens, symbols_list, decimals_list) for chain, tokens in Value_EVM_Balance_Checker.evm_tokens.items() if tokens]
        results = await asyncio.gather(*tasks)
        result = {chain: result for chain, result in zip(erc20_coins.keys(), results)}
        result = self.transform_dict(result)
        return result

    def send_result(self, result):
        small_wallets, small_wallets_value, balances, headers, send_table, total_value = [], [], {}, [[
            'number', 'wallet', '$value'], [], ['TOTAL_AMOUNTS', '', ''], ['TOTAL_VALUE', '']], [], []

        for number, (wallet, chains) in enumerate(result.items(), start=1):
            h_ = [number, wallet]
            wallet_value = 0

            for chain, coins in chains.items():
                for coin, balance in coins.items():
                    balance = round_to(balance)
                    symbol = coin.split('-')[0]
                    price = self.prices.get(symbol, 1)
                    value = int(balance * price)
                    wallet_value += value

                    head = f'{coin}-{chain.lower()}'

                    if head not in headers[0]:
                        headers[0].append(head)

                    h_.append(balance)

                    balances.setdefault(head, 0)
                    balances[head] += balance

                    if (
                        chain.lower() == Value_EVM_Balance_Checker.min_token_balance['chain'].lower() and
                        coin.lower() == Value_EVM_Balance_Checker.min_token_balance['coin'].lower() and
                        balance < Value_EVM_Balance_Checker.min_token_balance['amount']
                    ):
                        small_wallets.append(wallet)

            h_.insert(2, wallet_value)
            headers[1].append(h_)

            if wallet_value < Value_EVM_Balance_Checker.min_value_balance:
                small_wallets_value.append(wallet)

        for coin, balance in balances.items():
            balance = round_to(balance)
            symbol = coin.split('-')[0]
            price = self.prices.get(symbol, 1)
            value = int(balance * price)
            total_value.append(value)
            send_table.append([coin, balance, f'{value} $'])
            headers[2].append(round_to(balance)) # Record the total_amounts of each coin

        tokens = self.generate_csv(headers, send_table, total_value, small_wallets, small_wallets_value)

        cprint(f'\nAll balances :\n', 'blue')
        cprint(tokens, 'white')
        cprint(f'\nTOTAL_VALUE : {int(sum(total_value))} $', 'blue')
        cprint(f'\nResults written to file: results/{self.file_name}.csv\n', 'blue')

    def generate_csv(self, headers, send_table, total_value, small_wallets, small_wallets_value):
        with open(f'results/{self.file_name}.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(headers[0])
            spamwriter.writerows(headers[1])

            # send_table = [[coin, balance, f'{value} $'] for coin, balance, value in send_table]
            total_value = [str(value) for value in total_value]

            headers[3].insert(2, f'{int(sum(map(int, total_value)))} $')

            spamwriter.writerow([])
            spamwriter.writerows(headers[2:])

            spamwriter.writerow([])
            self.print_wallets(spamwriter, small_wallets, 'amount')
            spamwriter.writerow([])
            self.print_wallets(spamwriter, small_wallets_value, 'value')

            table_type = 'double_grid'
            head_table = ['token', 'amount', 'value']
            tokens = tabulate(send_table, head_table, tablefmt=table_type)

            return tokens

    def print_wallets(self, spamwriter, wallets, _type):
        if wallets:
            if _type == 'amount':
                small_text = f'{Value_EVM_Balance_Checker.min_token_balance["coin"]} [{Value_EVM_Balance_Checker.min_token_balance["chain"]}] balance on these wallets < {Value_EVM_Balance_Checker.min_token_balance["amount"]} :'
                spamwriter.writerow([small_text])
            elif _type == 'value':
                small_text = f'Value balance on these wallets < ${Value_EVM_Balance_Checker.min_value_balance} :'
                spamwriter.writerow([small_text])

            cprint(f'\n{small_text}', 'blue')
            for number, wallet in enumerate(wallets, start=1):
                cprint(wallet, 'white')
                spamwriter.writerow([number, wallet])

    async def start(self):
        await self.get_prices()
        evm_balances = await self.evm_balances()
        self.send_result(evm_balances)

class StarknetBalanceChecker:
    def __init__(self) -> None:
        self.file_name = 'starknet_balances'
        self.total_balance = {token:0 for token in Value_Starknet_Balance_Checker.starknet_tokens}

    async def fetch_price(self, session, symbol, url):
        try:
            async with session.get(url) as response:
                result = await response.json()
                price = result['USDT']
                self.prices[symbol] = float(price)
        except Exception as error:
            logger.error(f'{symbol}: error. Set price: 0')
            self.prices[symbol] = 0

    async def get_prices(self):
        logger.info('getting prices...')
        self.prices = {symbol: 0 for symbol in Value_Starknet_Balance_Checker.starknet_tokens}

        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in self.prices:
                url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
                tasks.append(self.fetch_price(session, symbol, url))
            await asyncio.gather(*tasks)

        logger.success('got prices')

    def send_result(self, result):
        small_wallets, small_wallets_value, send_table, total_value = [], [], [], []
        headers = ['number', 'wallet', '$value']
 
        for number, (wallet, tokens) in enumerate(result.items(), start=1):
            wallet_row = [number, wallet]
            wallet_value = 0

            token_balances = []

            for token, balance in tokens.items():
                balance = round_to(balance)
                self.total_balance[token] += balance
                price = self.prices.get(token, 1)
                value = round_to(balance * price)
                wallet_value += value
                token_balances.append(balance)
                if (token == Value_Starknet_Balance_Checker.min_token_balance['symbol'] and balance < Value_Starknet_Balance_Checker.min_token_balance['amount']):
                    small_wallets.append(wallet)

                if token not in headers:
                    headers.append(token)

            wallet_row.append(wallet_value)
            wallet_row.extend(token_balances)
            send_table.append(wallet_row)

            if wallet_value < Value_Starknet_Balance_Checker.min_value_balance:
                small_wallets_value.append(wallet)

        total_value = int(sum(wallet_row[2] for wallet_row in send_table))  # Assuming the wallet value is in the 3rd column
        send_table.insert(0, headers)  # Add the headers at the beginning of the table
        tokens = self.generate_csv(send_table, small_wallets, small_wallets_value)
        
        # Output results
        cprint(f'\nAll balances :\n', 'blue')
        cprint(tokens, 'white')

        cprint(f'\nTOTAL BALANCES', 'blue')
        for token, balance in self.total_balance.items():
            cprint(f'{token}: {round_to(balance)}', 'white')
        cprint(f'\nTOTAL VALUE : {total_value} $', 'blue')
        cprint(f'\nResults written to file: {self.file_name}.csv\n', 'white')

    def generate_csv(self, send_table, small_wallets, small_wallets_value):
        with open(f'results/{self.file_name}.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerows(send_table)

            spamwriter.writerow([])
            self.print_wallets(spamwriter, small_wallets, 'amount')
            spamwriter.writerow([])
            self.print_wallets(spamwriter, small_wallets_value, 'value')

        table_type = 'double_grid'  # Choose a format for the table output
        head_table = send_table.pop(0)  # Extract headers
        tokens = tabulate(send_table, headers=head_table, tablefmt=table_type)
        
        return tokens
    
    def print_wallets(self, spamwriter, wallets, _type):
        if wallets:
            if _type == 'amount':
                small_text = f'{Value_Starknet_Balance_Checker.min_token_balance["symbol"]} balance on these wallets < {Value_Starknet_Balance_Checker.min_token_balance["amount"]} :'
                spamwriter.writerow([small_text])
            elif _type == 'value':
                small_text = f'Value balance on these wallets < ${Value_Starknet_Balance_Checker.min_value_balance} :'
                spamwriter.writerow([small_text])

            cprint(f'\n{small_text}', 'blue')
            for number, wallet in enumerate(wallets, start=1):
                cprint(wallet, 'white')
                spamwriter.writerow([number, wallet])

    async def start(self):
        if STARKNET_ADDRESS:
            await self.get_prices()
            starknet_balances = await Starknet().main_balances(STARKNET_ADDRESS, Value_Starknet_Balance_Checker.starknet_tokens)
            self.send_result(starknet_balances)
        else:
            logger.error('Put starknet addresses in datas/starknet_address.txt')