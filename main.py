from config import RUN_TEXT, RUN_COLOR, WALLETS
from setting import RANDOM_WALLETS, CHECK_GWEI, TG_BOT_SEND , IS_SLEEP, SLEEP_FROM, SLEEP_TO

from modules.helpers import evm_wallet, list_send, wait_gas, send_msg, sleeping
from modules import *

from loguru import logger
from termcolor import cprint
import random


def start_module(module, key=''):

    if module == 1:
        cprint(f'\nstart : web3_checker\n', 'white')
        web3_check()

    if module == 2:
        cprint(f'\nstart : debank_checker\n', 'white')
        start_debank()

    if module == 3:
        cprint(f'\nstart : exchange_withdraw\n', 'white')
        exchange_withdraw(key)

    if module == 4:
        cprint(f'\nstart : okx_withdraw\n', 'white')
        okx_withdraw(key)

    if module == 5:
        cprint(f'\nstart : transfer\n', 'white')
        transfer(key)

    if module == 6:
        cprint(f'\nstart : 0x_swap\n', 'white')
        zeroX_swap(key)

    if module == 7:
        cprint(f'\nstart : orbiter_bridge\n', 'white')
        orbiter_bridge(key)

    if module == 8:
        cprint(f'\nstart : woofi_bridge\n', 'white')
        woofi_bridge(key)

    if module == 9:
        cprint(f'\nstart : woofi_swap\n', 'white')
        woofi_swap(key)

    if module == 10:
        cprint(f'\nstart : sushiswap\n', 'white')
        sushiswap(key)

    if module == 11:
        cprint(f'\nstart : bungee_refuel\n', 'white')
        bungee_refuel(key)

    if module == 12:
        cprint(f'\nstart : tx_checker\n', 'white')
        start_tx_check()

    if module == 13:
        cprint(f'\nstart : 1inch_swap\n', 'white')
        inch_swap(key)

    if module == 14:
        cprint(f'\nstart : merkly_refuel\n', 'white')
        merkly_refuel(key)
        

if __name__ == "__main__":

    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth\n', RUN_COLOR)

    MODULE = int(input('''
MODULE:
1.  web3_checker
2.  debank checker
3.  exchange withdraw : вывод с биржи
4.  okx withdraw
5.  transfer
6.  0x_swap
7.  orbiter finance
8.  woofi_bridge
9.  woofi_swap
10. sushiswap
11. bungee_refuel
12. tx_checker
13. 1inch_swap
14. merkly_refuel
                       
Выберите модуль (1 - 14) : '''))

    if MODULE in [1, 2, 12]:
        start_module(MODULE)

    else:

        if RANDOM_WALLETS == True: random.shuffle(WALLETS)

        zero = 0
        for key in WALLETS:
            zero += 1

            try:

                wallet = evm_wallet(key)
                list_send.append(f'{zero}/{len(WALLETS)} : {wallet}\n')
                cprint(f'\n{zero}/{len(WALLETS)} : {wallet}\n', 'white')

                if CHECK_GWEI == True:
                    wait_gas() # смотрим газ, если выше MAX_GWEI, ждем

                start_module(MODULE, key)

                if TG_BOT_SEND == True:
                    send_msg() # отправляем результат в телеграм
                list_send.clear()

                if IS_SLEEP == True:
                    sleeping(SLEEP_FROM, SLEEP_TO)

            except Exception as error:
                logger.error()

