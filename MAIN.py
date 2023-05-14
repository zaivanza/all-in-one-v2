import random

from loguru import logger
from termcolor import cprint

from config import RUN_TEXT, RUN_COLOR, WALLETS, settings, sleeping
from debank import start_debank
from web3_checker import web3_check
from utils import (exchange_withdraw,
                   okx_withdraw,
                   transfer,
                   inch_swap,
                   orbiter_bridge,
                   woofi,
                   evm_wallet,
                   list_send,
                   send_msg)


def start_module(module, key=''):
    modules = {
        1: web3_check,
        2: start_debank,
        3: exchange_withdraw,
        4: okx_withdraw,
        5: transfer,
        6: inch_swap,
        7: orbiter_bridge,
        8: woofi
    }

    modules[module](key)


if __name__ == "__main__":
    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth', RUN_COLOR)
    while True:
        try:
            MODULE = int(input('''
MODULE:

1. web3_checker
2. debank checker
3. exchange withdraw : вывод с биржи
4. okx withdraw : вывод с okx
5. transfer : вывод монет с кошельков
6. 1inch_swap : свапы на 1inch
7. orbiter finance : bridge нативных токенов
8. woofi : свапы / бриджи

Введите число от 1 до 8:'''))

            break
        except ValueError:
            pass

    if settings['RANDOM_WALLETS']:
        random.shuffle(WALLETS)

    total_wallets_len = len(WALLETS)
    for index, key in enumerate(WALLETS, start=1):

        try:
            wallet = evm_wallet(key)
            list_send.append(f'{index}/{total_wallets_len} : {wallet}\n')
            cprint(f'\n{index}/{total_wallets_len} : {wallet}\n', 'white')

            start_module(MODULE, key)

            if settings['TELEGRAM']['tg_bot_send']:
                send_msg()  # отправляем результат в телеграм
            list_send.clear()

            if settings['IS_SLEEP']:
                sleeping(settings['SLEEP_FROM'],
                         settings['SLEEP_TO'])
        except Exception as error:
            logger.error()
