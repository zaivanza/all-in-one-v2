import random

'''

MODULE :

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

'''

# ========================
MODULE = 2
# ========================

IS_SLEEP        = True # True / False. True если нужно поставить sleep между кошельками
# от скольки до скольки спим между кошельками (секунды) :
SLEEP_FROM      = 100
SLEEP_TO        = 200

# нужно ли рандомизировать (перемешивать) кошельки. True = да. False = нет
RANDOM_WALLETS  = True # True / False

RETRY = 0 # кол-во попыток при ошибках / фейлах

# настройка отправки результатов в тг бота
TG_BOT_SEND = True # True / False. Если True, тогда будет отправлять результаты

USE_PROXY   = False # True / False. True если хочешь юзать прокси

CHECK_GWEI  = True # True / False. если True, тогда будем смотреть base gwei, и если он больше MAX_GWEI, скрипт будет ожидать снижения газа
MAX_GWEI    = 50 # gas в gwei (смотреть здесь : https://etherscan.io/gastracker)

# если газ за транзу с этой сети будет выше в $, тогда скрипт будет спать 30с и пробовать снова
MAX_GAS_CHARGE = {
    'avalanche'     : 1,
    'polygon'       : 0.5,
    'ethereum'      : 3,
    'bsc'           : 0.3,
    'arbitrum'      : 1,
    'optimism'      : 1.5,
    'fantom'        : 0.5,
    'zksync'        : 1,
    'nova'          : 0.1,
    'gnosis'        : 0.1,
}


def value_web3_checker():

    '''
    чекер монет через web3
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync
    '''

    datas = {
        'bsc': [
            '', # BNB
            # '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d', # USDC
            '0x55d398326f99059ff775485246999027b3197955', # USDT
            ],
        'arbitrum': [
            '', # ETH
            # '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', # USDT
            # '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', # USDC
            ],
        # 'optimism': [
        #     '', # ETH
        #     '0x7f5c764cbc14f9669b88837ca1490cca17c31607', # USDC
        #     '0x4200000000000000000000000000000000000042', # OP
        #     '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', # USDT
        #     ],
        'polygon': [
            '', # MATIC
            ],
        # 'avalanche': [
        #     '', # AVAX
        #     ],
        # 'ethereum': [
        #     '', # ETH
        #     '0xdac17f958d2ee523a2206206994597c13d831ec7', # USDT
        #     ],
        'zksync': [
            '', # ETH
            ],
        # 'nova': [
        #     '', # ETH
        #     ],
        # 'fantom': [
        #     '', # FTM
        #     ],
    }

    min_balance = {
        'chain'     : 'zksync',
        'coin'      : 'ETH',
        'amount'    : 0.003 # если баланс меньше этого числа, кошелек будет выделен
    }
    
    file_name   = 'web3_balances' # имя файла в который будем сохранять данные. создается сам
    
    return datas, min_balance, file_name

def value_debank():

    '''
    чекер баланса через debank, смотрит все сети, протоколы и нфт.

    если кошельки ни разу не прогонял этим чекером, тогда сначала нужно их активировать : activate_wallets = True.
    сети, которые мы активируем, записаны в config.py => DEBANK_ACTIVATE_CHAINS. ненужные (как по мне) сети я закомментировал. если нужно, можешь их раскомментировать
    '''

    activate_wallets = True # True если нужно активировать кошельки (при первом запуске). False чтобы отключить

    # какие модули включены. если какой-то модуль не нужен, закомментируй (#) его. модуль nft самый долгий, по ненадобности лучше его отключать
    modules = [
        'token', # смотрит монеты
        # 'nft', # смотрит нфт
        # 'protocol' # смотрит протоколы
    ]

    # в каких сетях смотрим нфт. если какая-то сеть не нужна, закомментируй (#) ее
    nft_chains = [
        'op', 
        # 'eth', 
        # 'arb', 
        # 'matic', 
        # 'bsc'
        ]

    check_min_value     = 0 # $. если баланс монеты / протокола будет меньше этого числа, монета / протокол не будут записаны в файл
    check_chain         = '' # в какой сети ищем монету (отдельно выделит ее баланс)
    check_coin          = '' # какую монету ищем (отдельно выделит ее баланс)

    
    file_name = 'debank' # имя файла в который будем сохранять данные. создается сам
    
    return file_name, check_min_value, check_chain, check_coin, modules, nft_chains, activate_wallets

def value_exchange():

    '''
    withdraw coins from exchange.
    exchanges : binance | bybit | kucoin | mexc | huobi

    chains : 
    - binance : ETH | BEP20 | AVAXC | MATIC | ARBITRUM | OPTIMISM | APT
    - bybit
    - kucoin
    - mexc
    - huobi
    '''

    exchange    = 'binance' # запиши сюда биржу

    chain       = 'ETH' # в какой сети выводим
    symbol      = 'ETH'  # какой токен выводим

    amount_from = 0.015 # от какого кол-ва монет выводим
    amount_to   = 0.02 # до какого кол-ва монет выводим


    return exchange, chain, symbol, amount_from, amount_to

def value_okx():

    '''
    OKX
    BSC
    ERC20
    TRC20
    Polygon
    Avalanche C-Chain
    Avalanche X-Chain
    Arbitrum one
    Optimism
    Fantom
    '''

    chain       = 'Arbitrum one'
    symbol      = 'ETH'

    amount_from = 0.02
    amount_to   = 0.03

    account = 'account_1'

    FEE         = 0.0001 # комса на вывод
    SUB_ACC     = False # True / False

    return chain, symbol, amount_from, amount_to, account, FEE, SUB_ACC

def value_transfer():

    '''
    вывод (трансфер) монет с кошельков
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync
    '''

    chain                = 'arbitrum'   # в какой сети выводить
    token_address        = ''           # пусто если нативный токен сети

    amount_from          = 0.007            # от какого кол-ва монет делаем трансфер
    amount_to            = 0.007            # до какого кол-ва монет делаем трансфер  

    transfer_all_balance = True        # True / False. если True, тогда выводим весь баланс
    min_amount_transfer  = 0.0005            # если баланс будет меньше этого числа, выводить не будет
    keep_value_from      = 0.001            # от скольки монет оставляем на кошельке (работает только при : transfer_all_balance = True)
    keep_value_to        = 0.0015            # до скольки монет оставляем на кошельке (работает только при : transfer_all_balance = True)
    
    return chain, amount_from, amount_to, transfer_all_balance, min_amount_transfer, keep_value_from, keep_value_to, token_address

def value_0x_swap():

    '''
    свапы через апи 0x (агрегатор)
    docs : https://0x.org/docs/introduction/0x-cheat-sheet
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | celo
    '''

    chain               = 'bsc' # в какой сети свапаем
    from_token_address  = '' # пусто если нативный токен сети
    to_token_address    = '0x55d398326f99059ff775485246999027b3197955' # пусто если нативный токен сети

    amount_from         = 0.0001    # от какого кол-ва монет свапаем
    amount_to           = 0.0003    # до какого кол-ва монет свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    slippage = 1 # слиппейдж, дефолт от 1 до 3

    return chain, swap_all_balance, min_amount_swap, keep_value_from, keep_value_to, amount_from, amount_to, from_token_address, to_token_address, slippage

def value_orbiter():

    '''
    бридж нативных токенов через https://www.orbiter.finance/
    chains : zksync | polygon | ethereum | bsc | arbitrum | optimism | polygon_zkevm | nova | starknet
    минимальный бридж : 0.005
    '''

    from_chain          = 'nova'    # с какой сети 
    to_chain            = 'arbitrum'      # в какую сеть 

    amount_from         = 0.007 # от какого кол-ва монет делаем бридж
    amount_to           = 0.008 # до какого кол-ва монет делаем бридж

    bridge_all_balance  = False         # True / False. если True, тогда бриджим весь баланс
    min_amount_bridge   = 0          # если баланс будет меньше этого числа, выводить не будет
    keep_value_from     = 0.001             # от скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)
    keep_value_to       = 0.002             # до скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)

    return from_chain, to_chain, bridge_all_balance, amount_from, amount_to, min_amount_bridge, keep_value_from, keep_value_to

def value_woofi_bridge():

    '''
    бридж на https://fi.woo.org/ (бриджи идут через layerzero)
    chains : avalanche | polygon | ethereum | bsc | arbitrum | optimism | fantom
    '''
    
    from_chain          = 'polygon'
    to_chain            = 'arbitrum'  

    from_token          = '0xa8ce8aee21bc2a48a5ef670afcc9274c7bbbc035' # пусто если нативный токен сети
    to_token            = '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8' # пусто если нативный токен сети

    amount_from         = 0.001 # от какого кол-ва from_token свапаем
    amount_to           = 0.002 # до какого кол-ва from_token свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 3 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 4 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    
    return from_chain, to_chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to

def value_woofi_swap():

    '''
    свап на https://fi.woo.org/ 
    chains : avalanche | polygon | ethereum | bsc | arbitrum | optimism | fantom
    '''
    
    chain = 'fantom'

    from_token          = '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75' # пусто если нативный токен сети
    to_token            = '' # пусто если нативный токен сети

    amount_from         = 1 # от какого кол-ва from_token свапаем
    amount_to           = 2 # до какого кол-ва from_token свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    
    return chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to

def value_sushiswap():

    '''
    внимание! большие сайзы лучше свапать через 1inch или 0x

    свап на https://www.sushi.com/swap
    chains :  arbitrum | nova | bsc | polygon | fantom
    '''
    
    chain = 'nova'

    from_token          = '0x750ba8b76187092B0D1E87E28daaf484d1b5273b' # пусто если нативный токен сети
    to_token            = '' # пусто если нативный токен сети

    amount_from         = 0.00003 # от какого кол-ва from_token свапаем
    amount_to           = 0.00005 # до какого кол-ва from_token свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    slippage = 5 # советую ставить 1-5. если ошибка INSUFFICIENT_OUTPUT_AMOUNT , тогда увеличивай slippage

    return chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to, slippage

def value_bungee():

    '''
    refuel нативных токенов через https://www.bungee.exchange/
    chains : zksync | polygon | ethereum | bsc | arbitrum | optimism | fantom | polygon_zkevm | avalanche | gnosis
    '''

    from_chain          = 'gnosis' # с какой сети 
    to_chain            = 'polygon' # в какую сеть 

    amount_from         = 0.3 # от какого кол-ва монет делаем бридж
    amount_to           = 0.4 # до какого кол-ва монет делаем бридж

    bridge_all_balance  = False # True / False. если True, тогда бриджим весь баланс
    min_amount_bridge   = 0 # если баланс будет меньше этого числа, выводить не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)

    return from_chain, to_chain, bridge_all_balance, amount_from, amount_to, min_amount_bridge, keep_value_from, keep_value_to




