from web3 import Web3, AsyncHTTPProvider
from loguru import logger
from web3.eth import AsyncEth
import asyncio
from termcolor import cprint
from data.data import DATA
from .helpers import call_json, evm_wallet, func_chunks_generators
from config import outfile, WALLETS
from setting import value_tx_check
import csv
import time


nonces = {}
async def get_nonce(web3, wallet, chain):
    try:
            
        nonce = await web3.eth.get_transaction_count(Web3.to_checksum_address(wallet))
        nonces[wallet][chain] = nonce

    except Exception as error:
        logger.error(f'{chain} : {error}')
        await asyncio.sleep(3)
        return await get_nonce(web3, wallet, chain)

async def main(WALLETS, CHAINS):

    wallets_list = (list(func_chunks_generators(WALLETS, 100)))

    lens = 0
    for wallets in wallets_list:

        tasks = []

        for wallet in wallets:

            wallet = evm_wallet(wallet)

            nonces.update({wallet:{
                    'ethereum'      : 0,
                    'optimism'      : 0,
                    'bsc'           : 0,
                    'polygon'       : 0,
                    'polygon_zkevm' : 0,
                    'arbitrum'      : 0,
                    'avalanche'     : 0,
                    'fantom'        : 0,
                    'nova'          : 0,
                    'zksync'        : 0,
                    'celo'          : 0,
                    'gnosis'        : 0,
                    'core'          : 0,
                    'harmony'       : 0,
                }})

            for data in DATA.items():
                chain = data[0]
                rpc = data[1]['rpc']

                if chain in CHAINS:

                    web3 = Web3(
                        AsyncHTTPProvider(rpc),
                        modules={"eth": (AsyncEth,)},
                        middlewares=[],
                    )

                    task = asyncio.create_task(get_nonce(web3, wallet, chain))
                    tasks.append(task)

        await asyncio.gather(*tasks)

        lens = len(wallets) + lens
        cprint(f'{lens} / {len(WALLETS)} wallets', 'green')
        time.sleep(3)

def send_results(CHAINS):

    send_file = 'results/tx_checker.csv'

    low_nonces = {
        'ethereum'      : [],
        'optimism'      : [],
        'bsc'           : [],
        'polygon'       : [],
        'polygon_zkevm' : [],
        'arbitrum'      : [],
        'avalanche'     : [],
        'fantom'        : [],
        'nova'          : [],
        'zksync'        : [],
        'celo'          : [],
        'gnosis'        : [],
        'core'          : [],
        'harmony'       : [],
    }

    # записываем в csv
    with open(f'{outfile}{send_file}', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        headers = [['number', 'wallet'], []]

        zero = 0
        for data in nonces.items():
            zero += 1
            wallet = data[0]

            head = [zero, wallet]
            
            for chains in data[1].items():
                chain = chains[0]
                nonce = chains[1]

                if chain not in headers[0]:
                    headers[0].append(chain)

                head.append(nonce)
            
                if chain in CHAINS:
                    if nonce < CHAINS[chain]:
                        low_nonces[chain].append(wallet)
            
            headers[1].append(head)

        spamwriter.writerow(headers[0])
        for header in headers[1]:
            spamwriter.writerow(header)

        for items in low_nonces.items():
            chain   = items[0]
            wallets = items[1]

            if len(wallets) > 0:

                cprint(f'\nnonce in {chain} < {CHAINS[chain]}\n', 'blue')
                spamwriter.writerow([])
                spamwriter.writerow(['number', f'nonce in {chain} < {CHAINS[chain]}'])

                zero = 0
                for wallet in wallets:
                    zero += 1
                    cprint(wallet, 'white')
                    spamwriter.writerow([zero, wallet])

    cprint(f'\nРезультаты записаны в файл : {send_file}\n', 'blue')

def start_tx_check():

    chains = value_tx_check()

    asyncio.run(main(WALLETS, chains))

    send_results(chains)
