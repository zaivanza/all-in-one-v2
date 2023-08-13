from data.data import DATA
from config import WALLETS, outfile, ERC20_ABI
from setting import value_nft_checker
from .helpers import evm_wallet, round_to, check_balance

from loguru import logger
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import asyncio
from termcolor import cprint
import csv
from tabulate import tabulate


RESULT = {}

async def check_balance(web3, wallet, address_contract):
    try:

        try: 
            wallet = web3.eth.account.from_key(wallet).address
        except Exception as error: 
            wallet = wallet
            
        token_contract = web3.eth.contract(address=Web3.to_checksum_address(address_contract), abi=ERC20_ABI)
        balance = await token_contract.functions.balanceOf(web3.to_checksum_address(wallet)).call()

        return balance

    except Exception as error:
        logger.error(f'{error}')
        await asyncio.sleep(1)
        return await check_balance(web3, wallet, address_contract)

async def worker(wallet, chain, address_contract):

    web3 = Web3(
        AsyncHTTPProvider(DATA[chain]['rpc']),
        modules={"eth": (AsyncEth,)},
        middlewares=[],
    )

    balance = await check_balance(web3, wallet, address_contract)
    RESULT[wallet] = balance

async def main(contract, chain, wallets):

    tasks = [worker(wallet, chain, contract) for wallet in wallets]
    await asyncio.gather(*tasks)

def send_result(min_balance, file_name):

    small_wallets   = []
    total_amount    = []
    send_table      = []

    # записываем в csv
    with open(f'{outfile}results/{file_name}.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        spamwriter.writerow(['number', 'wallet', 'amount'])
        
        number = 0
        for data in RESULT.items():
            number += 1

            wallet = data[0]
            balance = data[1]
            spamwriter.writerow([number, wallet, balance])
            send_table.append([number, wallet, balance])

            if balance < min_balance:
                small_wallets.append(wallet)
            total_amount.append(balance)
        
        spamwriter.writerow([])
        spamwriter.writerow(['TOTAL AMOUNT', sum(total_amount)])

        table_type  = 'double_grid'
        head_table  = ['number', 'wallet', 'amount']
        tokens_     = tabulate(send_table, head_table, tablefmt=table_type)

        if len(small_wallets) > 0:
            small_text = f'nft balance of these wallets < {min_balance} :'
            cprint(small_text, 'blue')
            spamwriter.writerow([])
            spamwriter.writerow(['', small_text])
            number = 0
            for wallet in small_wallets:
                number += 1
                cprint(wallet, 'white')
                spamwriter.writerow([number, wallet])

        cprint(tokens_, 'white')
        cprint(f'\nTOTAL AMOUNT : {sum(total_amount)}', 'white')
        cprint(f'\nРезультаты записаны в файл : {outfile}results/{file_name}.csv\n', 'blue')


def nft_check():

    chain, contract, min_balance, file_name = value_nft_checker()

    wallets = []
    for key in WALLETS:
        wallet = evm_wallet(key)
        wallets.append(wallet)

        RESULT.update({wallet : 0})

    asyncio.run(main(contract, chain, wallets))
    send_result(min_balance, file_name)