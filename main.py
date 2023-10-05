from modules.utils.titles import TITLE, TITLE_COLOR
from setting import USE_TRACKS, TRACK
from runner import main, main_tracks
from termcolor import cprint
import asyncio

if __name__ == "__main__":

    cprint(TITLE, TITLE_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth', TITLE_COLOR)

    if USE_TRACKS:
        cprint('\nrun track :', 'white')
        for i, data in enumerate(TRACK):
            cprint(f'{i+1}. {data["module_name"]}', 'white')
        cprint('\n>>> press ENTER <<<', TITLE_COLOR)

        input()
        asyncio.run(main_tracks())
    else:
        MODULE = int(input('''
MODULE:
1.  web3_checker
2.  debank_checker
3.  exchange_withdraw
4.  okx_withdraw
5.  transfer
6.  0x_swap
7.  orbiter_finance
8.  woofi_bridge
9.  woofi_swap
10. sushiswap
11. bungee_refuel
12. tx_checker
13. 1inch_swap
14. merkly_refuel
15. nft_checker

Выберите модуль (1 - 15) : '''))

        asyncio.run(main(MODULE))

