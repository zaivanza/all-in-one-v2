'''

MODULE :

1. web3_checker
2. debank checker
3. exchange withdraw : вывод с биржи
4. okx withdraw : вывод с okx
5. transfer : вывод монет с кошельков
6. 1inch_swap : свапы на 1inch
7. orbiter finance : bridge нативных токенов
8. woofi : свапы / бриджи

'''

# ========================
MODULE = 1 # выбираем модуль от 1 до 8
# ========================

IS_SLEEP        = True # True / False. True если нужно поставить sleep между кошельками
# от скольки до скольки спим между кошельками (секунды) :
SLEEP_FROM      = 100 
SLEEP_TO        = 300

# нужно ли рандомизировать (перемешивать) кошельки. True = да. False = нет
RANDOM_WALLETS  = False # True / False

RETRY = 0 # кол-во попыток при ошибках / фейлах

# настройка отправки результатов в тг бота
TG_BOT_SEND = True # True / False. Если True, тогда будет отправлять результаты
TG_TOKEN    = '' # токен от тг-бота
TG_ID       = 0 # id твоего телеграмма

# апи ключи от бирж. если биржей не пользуешься, можно не вставлять
CEX_KEYS = {
    'binance'   : {'api_key': '', 'api_secret': ''},
    'mexc'      : {'api_key': '', 'api_secret': ''},
    'kucoin'    : {'api_key': '', 'api_secret': '', 'password': ''},
    'huobi'     : {'api_key': '', 'api_secret': ''},
    'bybit'     : {'api_key': '', 'api_secret': ''},
    'okx'       : {'api_key': '', 'api_secret': '', 'password': ''},
}

def value_web3_checker():

    '''
    чекер монет через web3, смотрит по 1 монете в конкретной сети
    '''

    chain               = 'arbitrum' # в какой сети смотрим
    address_contract    = '' # адреса монеты. пусто если нативная монета.
    min_balance         = 0 # по дефолту = 0. если баланс < этого числа, кошелек будет помечен

    file_name           = 'web3_balances' # имя файла в который будем сохранять данные. создается сам
    
    return chain, address_contract, min_balance, file_name

def value_debank():

    '''
    чекер баланса через debank, смотрит все сети, протоколы и нфт
    '''

    # какие модули включены. если какой-то модуль не нужен, закомментируй (#) его. модуль nft самый долгий, по ненадобности лучше его отключать
    modules = [
        'token', # смотрит монеты
        'nft', # смотрит нфт
        'protocol' # смотрит протоколы
    ]

    # в каких сетях смотрим нфт. если какая-то сеть не нужна, закомментируй (#) ее
    nft_chains = [
        'op', 
        'eth', 
        # 'arb', 
        # 'matic', 
        # 'bsc'
        ]

    check_min_value     = 5 # $. если баланс монеты / протокола будет меньше этого числа, монета / протокол не будут записаны в файл
    check_chain         = 'ARB' # в какой сети ищем монету (отдельно выделит ее баланс)
    check_coin          = 'ETH' # какую монету ищем (отдельно выделит ее баланс)

    
    file_name = 'debank' # имя файла в который будем сохранять данные. создается сам
    
    return file_name, check_min_value, check_chain, check_coin, modules, nft_chains

def value_exchange():

    '''
    withdraw coins from exchange.
    exchanges : binance | bybit | kucoin | mexc | huobi

    chains : 
    - binance   : ETH | BEP20 | AVAXC | MATIC | ARBITRUM | OPTIMISM | APT
    - bybit     : ...
    - kucoin    : ...
    - mexc      : ...
    - huobi     : ...
    '''

    exchange    = 'binance' # запиши сюда биржу

    chain       = 'BEP20' # в какой сети выводим
    symbol      = 'USDT'  # какой токен выводим

    amount_from = 13 # от какого кол-ва монет выводим
    amount_to   = 20 # до какого кол-ва монет выводим


    return exchange, chain, symbol, amount_from, amount_to

def value_okx():

    '''
    выводит только с funding, есть вывод с суб-аккаунтов

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

    chain       = 'Arbitrum one' # с какой сети выводить
    symbol      = 'ETH' # какую монету выводить

    amount_from = 0.1 # выводим от
    amount_to   = 0.2 # выводим до

    FEE         = 0.0001 # комиссия на вывод
    SUB_ACC     = True # True / False. True если нужно выводить с суб-аккаунтов

    API_KEY     = CEX_KEYS['okx']['api_key']
    API_SECRET  = CEX_KEYS['okx']['api_secret']
    PASSWORD    = CEX_KEYS['okx']['password']

    return chain, symbol, amount_from, amount_to, API_KEY, API_SECRET, PASSWORD, FEE, SUB_ACC

def value_transfer():

    '''
    вывод (трансфер) монет с кошельков
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync
    '''

    chain                = 'arbitrum'   # в какой сети выводить
    token_address        = ''           # пусто если нативный токен сети

    amount_from          = 1            # от какого кол-ва монет делаем трансфер
    amount_to            = 2            # до какого кол-ва монет делаем трансфер  

    transfer_all_balance = False        # True / False. если True, тогда выводим весь баланс
    min_amount_transfer  = 0            # если баланс будет меньше этого числа, выводить не будет
    keep_value_from      = 0            # от скольки монет оставляем на кошельке (работает только при : transfer_all_balance = True)
    keep_value_to        = 0            # до скольки монет оставляем на кошельке (работает только при : transfer_all_balance = True)
    
    return chain, amount_from, amount_to, transfer_all_balance, min_amount_transfer, keep_value_from, keep_value_to, token_address

def value_1inch_swap():

    '''
    свапы на 1inch
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync
    '''

    chain               = 'zksync' # в какой сети свапаем
    from_token_address  = '' # пусто если нативный токен сети
    to_token_address    = '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4' # пусто если нативный токен сети

    amount_from         = 0.0001    # от какого кол-ва монет свапаем
    amount_to           = 0.0002    # до какого кол-ва монет свапаем

    swap_all_balance    = False     # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0         # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0         # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0         # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    slippage = 3 # слиппейдж, дефолт от 1 до 3

    divider_zksync = 3 # на сколько делим gasLimit в zksync : советую ставить 3-4. исполняется только на zksync

    return chain, swap_all_balance, min_amount_swap, keep_value_from, keep_value_to, amount_from, amount_to, from_token_address, to_token_address, slippage, divider_zksync

def value_orbiter():

    '''
    бридж нативных токенов через https://www.orbiter.finance/
    chains : zksync | polygon | ethereum | bsc | arbitrum | optimism | polygon_zkevm | nova

    минимальный бридж : 0.005
    '''

    from_chain          = 'arbitrum'    # с какой сети 
    to_chain            = 'zksync'      # в какую сеть 

    amount_from         = 0.015 # от какого кол-ва монет делаем бридж
    amount_to           = 0.02 # до какого кол-ва монет делаем бридж

    bridge_all_balance  = False         # True / False. если True, тогда бриджим весь баланс
    min_amount_bridge   = 0.01          # если баланс будет меньше этого числа, выводить не будет
    keep_value_from     = 0             # от скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)
    keep_value_to       = 0             # до скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)

    return from_chain, to_chain, bridge_all_balance, amount_from, amount_to, min_amount_bridge, keep_value_from, keep_value_to

def value_woofi():

    '''
    свап / бридж на https://fi.woo.org/ (бриджи идут через layerzero)
    chains : avalanche | polygon | ethereum | bsc | arbitrum | optimism | fantom
    '''
    
    from_chain          = 'arbitrum'
    to_chain            = 'bsc' 

    from_token          = '' # пусто если нативный токен сети
    to_token            = '' # пусто если нативный токен сети

    amount_from         = 2       # от какого кол-ва from_token свапаем
    amount_to           = 3       # до какого кол-ва from_token свапаем

    swap_all_balance    = False         # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0             # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0             # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0             # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    
    return from_chain, to_chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to

