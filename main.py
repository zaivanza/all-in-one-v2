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
1.  evm_balance_checker
2.  starknet_balance_checker
3.  debank_checker
4.  exchange_withdraw
5.  okx_withdraw
6.  transfer
7.  0x_swap
8.  orbiter_finance
9.  woofi_bridge
10. woofi_swap
11. sushiswap
12. bungee_refuel
13. tx_checker
14. 1inch_swap
15. zerius_refuel
16. nft_checker
17. zerius_onft
18. starkgate_bridge
19. base_bridge 
20. arbitrum_bridge
21. zora_bridge
22. zksync_bridge

Choose a module (1 - 22) : '''))

        asyncio.run(main(MODULE))

