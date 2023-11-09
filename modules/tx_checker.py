from datas.data import DATA
from .utils.helpers import func_chunks_generators
from config import WALLETS
from setting import Value_Txn_Checker

from web3 import Web3, AsyncHTTPProvider
from loguru import logger
from web3.eth import AsyncEth
import asyncio
from termcolor import cprint
import csv
import time

class TxChecker:

    def __init__(self):
        self.nonces = {}
        self.send_file = 'results/tx_checker.csv'

    def get_address(self, wallet):
        try:
            web3 = Web3(Web3.HTTPProvider(DATA['ethereum']['rpc']))
            wallet = web3.eth.account.from_key(wallet).address
        except:
            wallet = wallet
        return wallet

    async def get_nonce(self, web3, wallet, chain):
        try:
            nonce = await web3.eth.get_transaction_count(Web3.to_checksum_address(wallet))
            self.nonces[wallet][chain] = nonce
        except Exception as error:
            logger.error(f'{chain} : {error}')
            await asyncio.sleep(3)
            return await self.get_nonce(web3, wallet, chain)

    async def fetch_nonces(self, wallets):
        tasks = []
        for wallet in wallets:
            wallet = self.get_address(wallet)
            self.nonces[wallet] = {chain: 0 for chain in Value_Txn_Checker.chains}
            for chain in Value_Txn_Checker.chains:
                web3 = self.get_web3(chain)
                task = asyncio.create_task(self.get_nonce(web3, wallet, chain))
                tasks.append(task)
        await asyncio.gather(*tasks)

    async def main(self):
        wallets_list = list(func_chunks_generators(WALLETS, 100))
        lens = 0
        for wallets in wallets_list:
            await self.fetch_nonces(wallets)
            lens += len(wallets)
            cprint(f'{lens} / {len(WALLETS)} wallets', 'green')
            time.sleep(3)

    def get_web3(self, chain):
        web3 = Web3(AsyncHTTPProvider(DATA[chain]['rpc']), modules={"eth": AsyncEth}, middlewares=[])
        return web3

    def write_csv(self):
        low_nonces = {chain: [] for chain in Value_Txn_Checker.chains}
        headers = [['number', 'wallet'], []]

        with open(self.send_file, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            zero = 0
            for wallet, chain_nonces in self.nonces.items():
                zero += 1
                head = [zero, wallet]

                for chain, nonce in chain_nonces.items():
                    if chain not in headers[0]:
                        headers[0].append(chain)
                    head.append(nonce)

                    if chain in Value_Txn_Checker.chains and nonce < Value_Txn_Checker.chains[chain]:
                        low_nonces[chain].append(wallet)

                headers[1].append(head)

            spamwriter.writerow(headers[0])
            for header in headers[1]:
                spamwriter.writerow(header)

            for chain, wallets in low_nonces.items():
                if wallets:
                    cprint(f'\nnonce in {chain} < {Value_Txn_Checker.chains[chain]}\n', 'blue')
                    spamwriter.writerow([])
                    spamwriter.writerow(['number', f'nonce in {chain} < {Value_Txn_Checker.chains[chain]}'])

                    zero = 0
                    for wallet in wallets:
                        zero += 1
                        cprint(wallet, 'white')
                        spamwriter.writerow([zero, wallet])

        cprint(f'\nРезультаты записаны в файл : {self.send_file}\n', 'blue')

    async def start(self):
        await self.main()
        self.write_csv()
