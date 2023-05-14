from config import *
from utils import *
from web3_checker import *
from debank import *

def start_module(module, key=''):

    if module == 1:
        web3_check()

    if module == 2:
        start_debank()

    if module == 3:
        exchange_withdraw(key)

    if module == 4:
        okx_withdraw(key)

    if module == 5:
        transfer(key)

    if module == 6:
        inch_swap(key)

    if module == 7:
        orbiter_bridge(key)

    if module == 8:
        woofi(key)


if __name__ == "__main__":

    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth\n', RUN_COLOR)

    MODULE = int(MODULE)

    if MODULE in [1, 2]:
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

                start_module(MODULE, key)

                if TG_BOT_SEND == True:
                    send_msg() # отправляем результат в телеграм
                list_send.clear()

                if IS_SLEEP == True:
                    sleeping(SLEEP_FROM, SLEEP_TO)

            except Exception as error:
                logger.error()

        
