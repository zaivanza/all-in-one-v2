from .utils.helpers import func_chunks_generators, round_to
from .utils.files import call_json
from datas.data import DATA
from config import PROXIES, WALLETS, DEBANK_ACTIVATE_CHAINS
from setting import Value_DeBank

import time
from loguru import logger
import asyncio, aiohttp
from termcolor import cprint
import random
import csv
from tabulate import tabulate
from web3 import Web3

class DeBank:

    def __init__(self):
        self.get_result = {
            module: {chain: {} for chain in (Value_DeBank.nft_chains if module == 'nft' else [])}
            for module in Value_DeBank.modules
        }
        self.wallets = [self.get_address(key) for key in WALLETS]
        self.file_name = "debank"

    async def get_debank(self, session, address, type_, chain=''):

        urls = {
            'token'     : f'https://api.debank.com/token/cache_balance_list?user_addr={address}',
            'nft'       : f'https://api.debank.com/nft/collection_list?user_addr={address}&chain={chain}',
            'protocol'  : f'https://api.debank.com/portfolio/project_list?user_addr={address}',
        }

        while True:
            try:
                proxy = random.choice(PROXIES)
                sleep = 3

                async with session.get(urls[type_], proxy=proxy, timeout=10) as resp:

                    if resp.status == 200:
                        resp_json = await resp.json(content_type=None)
                        if type_ == 'nft': 
    
                            if resp_json['data']['job']: 
                                await asyncio.sleep(sleep)
                            else:

                                self.get_result[type_][chain].update({address : resp_json})
                                logger.success(f'{address} | {type_} : {chain}')
                                break

                        else:
                            
                            self.get_result[type_].update({address : resp_json})
                            logger.success(f'{address} | {type_}')
                            break
                    else:
                        # logger.info(f'resp.status = {resp.status}, try again in {sleep} sec.')
                        await asyncio.sleep(sleep)

            except Exception as error:
                logger.info(f'{address} | {type_} : {error}, try again in {sleep} sec.')
                await asyncio.sleep(3)

    async def checker_main(self):

        async with aiohttp.ClientSession() as session:
            wallets_list = (list(func_chunks_generators(self.wallets, 50)))

            for items in wallets_list:

                tasks = []
                for address in items:

                    if 'token' in Value_DeBank.modules:
                        tasks.append(asyncio.create_task(self.get_debank(session, address, 'token')))

                    if 'protocol' in Value_DeBank.modules:
                        tasks.append(asyncio.create_task(self.get_debank(session, address, 'protocol')))
                        
                    if 'nft' in Value_DeBank.modules:
                        for chain in Value_DeBank.nft_chains:
                            tasks.append(asyncio.create_task(self.get_debank(session, address, 'nft', chain)))

                await asyncio.gather(*tasks)

    def get_json_data(self):

        total_result = {}

        for wallet in self.wallets:
            total_result.update({wallet : {
                'token' : [],
                'nft' : [],
                'protocol' : [],
                'protocol_value' : 0,
                'token_value' : 0,
                'total_value' : 0,
            }})

        # check tokens
        if 'token' in self.get_result:
            for tokens in self.get_result['token'].items():
                
                wallet  = tokens[0]
                data    = tokens[1]

                for items in data['data']:

                    chain   = items['chain'].upper()
                    price   = items['price']
                    amount  = items['amount']
                    symbol  = items['optimized_symbol']
                    value   = amount * price
                    
                    if value > Value_DeBank.check_min_value:

                        total_result[wallet]['token'].append(
                            {
                                'chain'     : chain,
                                'symbol'    : symbol,
                                'amount'    : amount,
                                'value'     : value,
                            }
                        )

                        total_result[wallet]['token_value'] += value

        # check nfts
        if 'nft' in self.get_result:
            for nfts in self.get_result['nft'].items():

                chain = nfts[0].upper()
                data_ = nfts[1]
                
                for w_ in data_.items():

                    wallet  = w_[0]
                    data    = w_[1]

                    for items in data['data']['result']['data']:

                        amount  = items['amount']
                        name    = items['name']

                        total_result[wallet]['nft'].append(
                            {
                                'chain'     : chain,
                                'name'      : name,
                                'amount'    : amount,
                            }
                        )

        # check protocols
        if 'protocol' in self.get_result:
            for tokens in self.get_result['protocol'].items():
                
                wallet  = tokens[0]
                data    = tokens[1]

                for items in data['data']:

                    chain   = items['chain'].upper()
                    name    = items['name']
                    value   = int(items['portfolio_item_list'][0]['stats']['asset_usd_value'])
                    
                    if value > Value_DeBank.check_min_value:

                        total_result[wallet]['protocol'].append(
                            {
                                'chain'     : chain,
                                'name'      : name,
                                'value'     : value,
                            }
                        )

                        total_result[wallet]['protocol_value'] += value

        # check total value
        for wallet in self.wallets:
            total_result[wallet]['total_value'] = total_result[wallet]['protocol_value'] + total_result[wallet]['token_value']

        return total_result

    def send_result(self):

        json_data = self.get_json_data()

        file = open(f'results/{self.file_name}.txt', 'w', encoding='utf-8')

        with open(f'results/{self.file_name}.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(['number', 'wallet', 'balance $', 'protocols $', 'tokens $', 'nft amount'])

            all_wallets_value = []
            all_finder_token = []

            zero = 0
            for wallets in json_data.items():
                zero+= 1

                wallet = wallets[0]
                data = wallets[1]

                file.write(f'\n{zero}. {wallet}\n')

                tokens = []
                for items in data['token']:

                    chain   = items['chain']
                    symbol  = items['symbol']
                    amount  = round_to(items['amount'])
                    value   = int(items['value'])

                    tokens.append([chain, amount, symbol, f'{value} $'])

                    if Value_DeBank.check_chain != '':
                        if Value_DeBank.check_chain == chain:
                            if Value_DeBank.check_coin == symbol:
                                finder = amount
                    else:
                            if Value_DeBank.check_coin == symbol:
                                finder = amount

                protocols = []
                for items in data['protocol']:

                    chain   = items['chain']
                    name    = items['name']
                    value   = int(items['value'])

                    protocols.append([chain, name, f'{value} $'])

                nfts = []
                nft_amounts = []
                for items in data['nft']:

                    chain   = items['chain']
                    name    = items['name']
                    amount  = int(items['amount'])

                    nft_amounts.append(amount)
                    nfts.append([chain, name, amount])

                protocol_value  = int(data['protocol_value'])
                token_value     = int(data['token_value'])
                total_value     = int(data['total_value'])

                table_type  = 'double_outline'

                head_table  = ['chain', 'amount', 'symbol', 'value']
                tokens_     = tabulate(tokens, head_table, tablefmt=table_type)

                head_table  = ['chain', 'name', 'value']
                protocols_  = tabulate(protocols, head_table, tablefmt=table_type)

                head_table  = ['chain', 'name', 'amount']
                nfts_       = tabulate(nfts, head_table, tablefmt=table_type)


                cprint(f'\n{zero}. {wallet}\n', 'yellow')

                if len(tokens) > 0:
                    file.write(f'\n{tokens_}\n')
                    cprint(tokens_, 'white')

                if len(protocols) > 0:
                    file.write(f'\n{protocols_}\n')
                    cprint(protocols_, 'white')

                if len(nfts) > 0:
                    file.write(f'\n{nfts_}\n')
                    cprint(nfts_, 'white')

                file.write(f'\ntotal_value : {total_value} $\n')
                cprint(f'\ntotal_value : {total_value} $\n', 'green')
                

                if Value_DeBank.check_coin != '':
                    try:
                        file.write(f'{Value_DeBank.check_coin} : {finder}\n')
                        cprint(f'{Value_DeBank.check_coin} : {finder}\n', 'green')
                        all_finder_token.append(finder)
                    except : None
                    

                spamwriter.writerow([zero, wallet, total_value, protocol_value, token_value, sum(nft_amounts)])

                all_wallets_value.append(total_value)

            cprint(f'\n>>> ALL WALLETS VALUE : {sum(all_wallets_value)} $ <<<\n', 'blue')
            file.write(f'\n>>> ALL WALLETS VALUE : {sum(all_wallets_value)} $ <<<\n')
            spamwriter.writerow(['TOTAL_VALUE :', f'{sum(all_wallets_value)}$'])

            amount_finder_coin = round_to(sum(all_finder_token))
            if amount_finder_coin > 0:
                cprint(f'\n>>> {Value_DeBank.check_coin} : {amount_finder_coin} $ <<<\n', 'blue')
                file.write(f'\n>>> {Value_DeBank.check_coin} : {amount_finder_coin} $ <<<\n')
                spamwriter.writerow([f'{Value_DeBank.check_coin}', amount_finder_coin])

        file.close()

        cprint(f'Результаты записаны в файлы : {self.file_name}.csv и {self.file_name}.txt\n', 'blue')

    async def get_activate_debank(self, session, wallet, chain):

        while True:
            try:

                sleep   = 3
                proxy   = random.choice(PROXIES)
                url     = f'https://api.debank.com/token/balance_list?user_addr={wallet}&chain={chain[0]}'

                async with session.get(url, proxy=proxy, timeout=10) as resp:

                    if resp.status == 200:
                        logger.success(f'{wallet} | {chain[1]}')
                        break
                    else:
                        # logger.info(f'response_status : {resp.status}, try again in {sleep} sec.')
                        await asyncio.sleep(sleep)

            except Exception as error:
                logger.info(f'{wallet} | {chain[1]} : {error}, try again in {sleep} sec.')
                await asyncio.sleep(sleep)

    async def activate_wallet_debank(self, chains):

        async with aiohttp.ClientSession() as session:

            wallets_list = (list(func_chunks_generators(self.wallets, 50)))
            for items in wallets_list:

                tasks = []
                for wallet in items:

                    for items in chains:
                        for chain in items.items():
                            tasks.append(asyncio.create_task(self.get_activate_debank(session, wallet, chain)))

                await asyncio.gather(*tasks)

    def get_address(self, key):
        try:
            web3 = Web3(Web3.HTTPProvider(DATA["ethereum"]["rpc"]))
            address = web3.eth.account.from_key(key).address
        except:
            address = key
        return address

    async def start(self):

        start_time = time.perf_counter()

        if Value_DeBank.activate_wallets:
            print()
            logger.info('start activating wallets')
            print()
            await self.activate_wallet_debank(DEBANK_ACTIVATE_CHAINS)

        print()
        logger.info('start checking wallets')
        print()

        await self.checker_main()
        self.send_result()

        fin = round((time.perf_counter() - start_time), 1)
        cprint(f'finish : {int(fin)} sec.', 'white')
        print()


