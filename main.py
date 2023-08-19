from config import RUN_TEXT, RUN_COLOR, WALLETS
from setting import RANDOM_WALLETS, CHECK_GWEI, TG_BOT_SEND , IS_SLEEP, SLEEP_FROM, SLEEP_TO, USE_TRACKS, TRACK

from modules.helpers import evm_wallet, list_send, wait_gas, send_msg, sleeping, wait_balance
from modules import *

from loguru import logger
from termcolor import cprint
import random


def start_module(module, key='', params=None):

    if module == 1:
        cprint(f'\nstart : web3_checker\n', 'white')
        result = web3_check()

    if module == 2:
        cprint(f'\nstart : debank_checker\n', 'white')
        result = start_debank()

    if module == 3:
        cprint(f'\nstart : exchange_withdraw\n', 'white')
        result = exchange_withdraw(key, params)

    if module == 4:
        cprint(f'\nstart : okx_withdraw\n', 'white')
        result = okx_withdraw(key, params)

    if module == 5:
        cprint(f'\nstart : transfer\n', 'white')
        result = transfer(key, params)

    if module == 6:
        cprint(f'\nstart : 0x_swap\n', 'white')
        result = zeroX_swap(key, params)

    if module == 7:
        cprint(f'\nstart : orbiter_bridge\n', 'white')
        result = orbiter_bridge(key, params)

    if module == 8:
        cprint(f'\nstart : woofi_bridge\n', 'white')
        result = woofi_bridge(key, params)

    if module == 9:
        cprint(f'\nstart : woofi_swap\n', 'white')
        result = woofi_swap(key, params)

    if module == 10:
        cprint(f'\nstart : sushiswap\n', 'white')
        result = sushiswap(key, params)

    if module == 11:
        cprint(f'\nstart : bungee_refuel\n', 'white')
        result = bungee_refuel(key, params)

    if module == 12:
        cprint(f'\nstart : tx_checker\n', 'white')
        result = start_tx_check()

    if module == 13:
        cprint(f'\nstart : 1inch_swap\n', 'white')
        result = inch_swap(key, params)
    
    if module == 14:
        cprint(f'\nstart : merkly_refuel\n', 'white')
        result = merkly_refuel(key, params)

    if module == 15:
        cprint(f'\nstart : nft_checker\n', 'white')
        result = nft_check()

    return result


if __name__ == "__main__":

    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth\n', RUN_COLOR)

    if RANDOM_WALLETS == True: random.shuffle(WALLETS)

    if USE_TRACKS == True:

        cprint('\n>>> running track. press ENTER <<<', 'white')
        input()
        
        number = 0
        for key in WALLETS:
            number += 1

            try:

                wallet = evm_wallet(key)
                list_send.append(f'{number}/{len(WALLETS)} : {wallet}\n')
                cprint(f'\n{number}/{len(WALLETS)} : {wallet}\n', 'white')

                if CHECK_GWEI == True:
                    wait_gas() # смотрим газ, если выше MAX_GWEI, ждем

                for params in TRACK:

                    if params['module_name'] == 'wait_balance':
                        wait_balance(key, params['params']['chain'], params['params']['min_balance'], params['params']['token'])
                    
                    elif params['module_name'] == 'sleeping':
                        sleeping(int(params['params']['from']), int(params['params']['to']))
                    
                    else:
                        result = start_module(params['module_number'], key, params['params'])
                        if result != "success": 
                            logger.error('Module is not success, cycle broken')
                            break

                if TG_BOT_SEND == True:
                    send_msg() # отправляем результат в телеграм
                list_send.clear()

                if IS_SLEEP == True:
                    sleeping(SLEEP_FROM, SLEEP_TO)

            except Exception as error:
                logger.error()

    else:
 
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
15. nft_checker

Выберите модуль (1 - 15) : '''))

        if MODULE in [1, 2, 12, 15]:
            start_module(MODULE)

        else:

            cprint(f'\n>>> running module {MODULE}. press ENTER <<<', 'white')
            input()

            number = 0
            for key in WALLETS:
                number += 1

                try:

                    wallet = evm_wallet(key)
                    list_send.append(f'{number}/{len(WALLETS)} : {wallet}\n')
                    cprint(f'\n{number}/{len(WALLETS)} : {wallet}\n', 'white')

                    if CHECK_GWEI == True:
                        wait_gas() # смотрим газ, если выше MAX_GWEI, ждем

                    result = start_module(MODULE, key)

                    if TG_BOT_SEND == True:
                        send_msg() # отправляем результат в телеграм
                    list_send.clear()

                    if IS_SLEEP == True:
                        if result == "success": # если действие выполнено - спим
                            sleeping(SLEEP_FROM, SLEEP_TO)

                except Exception as error:
                    logger.error()

