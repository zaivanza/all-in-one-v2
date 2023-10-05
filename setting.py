from tracks import *

# --- Настройки ---
WALLETS_IN_BATCH = 1    # Сколько кошельков запускаем в одном потоке (одновременно)

USE_TRACKS = False      # Включить/выключить треки
TRACK = track_1         # Меняется на переменную трека из routes.py

IS_SLEEP = True         # Включить/выключить задержку между кошельками
DELAY_SLEEP = [10, 30]  # Диапазон задержки между кошельками (секунды)
RANDOMIZER = False      # Включить/выключить случайное перемешивание кошельков
RETRY = 0               # Количество попыток при ошибках/фейлах
TG_BOT_SEND = True      # Включить/выключить отправку результатов в Telegram-бота

USE_PROXY = False       # Включить/выключить использование прокси в запросах к web3
CHECK_GWEI = True       # Включить/выключить проверку base Gwei
MAX_GWEI = 25           # Максимальный Gwei (см. https://etherscan.io/gastracker)

# Максимальная комиссия для транзакции в USD, при которой скрипт будет спать 30 секунд и пытаться снова
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
    'celo'          : 0.1,
    'polygon_zkevm' : 0.5,
    'core'          : 0.1,
    'harmony'       : 0.1,
}

class Value_Web3_Checker:

    '''
    чекер монет через web3
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync | polygon_zkevm | celo | gnosis | core | harmony | linea | base
    '''

    datas = {
        'bsc': [
            '', # BNB
            '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d', # USDC
            '0x55d398326f99059ff775485246999027b3197955', # USDT
            '0xe9e7cea3dedca5984780bafc599bd69add087d56', # BUSD
            '0xB0b84D294e0C75A6abe60171b70edEb2EFd14A1B', # SnBNB
            ],
        'arbitrum': [
            '', # ETH
            '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', # USDT
            '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', # USDC
            '0x6694340fc020c5e6b96567843da2df01b2ce1eb6', # STG
            ],
        'optimism': [
            '', # ETH
            '0x7f5c764cbc14f9669b88837ca1490cca17c31607', # USDC
            '0x4200000000000000000000000000000000000042', # OP
            '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', # USDT
            ],
        'polygon': [
            '', # MATIC
            '0xc2132d05d31c914a87c6611c10748aeb04b58e8f', # USDT
            '0x2791bca1f2de4661ed88a30c99a7a9449aa84174', # USDC
            ],
        'avalanche': [
            '', # AVAX
            '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7', # USDT
            ],
        'ethereum': [
            '', # ETH
            '0xdac17f958d2ee523a2206206994597c13d831ec7', # USDT
            '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', # USDC
            '0xaf5191b0de278c7286d6c7cc6ab6bb8a73ba2cd6', # STG
            ],
        'zksync': [
            '', # ETH
            ],
        'nova': [
            '', # ETH
            ],
        # 'fantom': [
        #     '', # FTM
        #     ],
        # 'polygon_zkevm': [
        #     '', # ETH
        #     ],
        # 'celo': [
        #     '', # CELO
        #     ],
        # 'gnosis': [
        #     '', # xDAI
        #     ],
        # 'harmony': [
        #     '', # ONE
        #     ],
        # 'core': [
        #     '', # CORE
        #     ],
        # 'linea': [
        #     '', # ETH
        #     ],
        # 'base': [
        #     '', # ETH
        #     ],
    }

    min_token_balance = {
        'chain'     : 'bsc',
        'coin'      : 'BNB',
        'amount'    : 0 # если баланс меньше этого числа, кошелек будет выделен
    }

    min_value_balance = 5 # если баланс кошелька в $ меньше этого числа, кошелек будет выделен
    
class Value_DeBank():

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
        'protocol' # смотрит протоколы
    ]

    # в каких сетях смотрим нфт. если какая-то сеть не нужна, закомментируй (#) ее
    nft_chains = [
        'op', 
        'eth', 
        # 'arb', 
        # 'matic', 
        # 'bsc',
        'base'
        ]

    check_min_value     = 1 # $. если баланс монеты / протокола будет меньше этого числа, монета / протокол не будут записаны в файл
    check_chain         = '' # в какой сети ищем монету (отдельно выделит ее баланс)
    check_coin          = '' # какую монету ищем (отдельно выделит ее баланс)    

class Value_Exchange():

    '''
    withdraw coins from exchange.
    exchanges : binance | bybit | kucoin | mexc | huobi | bitget

    chains : 
    - binance : ETH | BEP20 | AVAXC | MATIC | ARBITRUM | OPTIMISM | APT
    - bybit
    - kucoin
    - mexc
    - huobi
    - bitget : zkSyncEra | ArbitrumNova | ArbitrumOne | ETH / ERC20 | Optimism | BEP20 | TRC20 | Polygon | Aptos | CELO | CoreDAO | Harmony
    '''

    exchange    = 'binance' # запиши сюда биржу

    chain       = 'BUSD' # в какой сети выводим
    symbol      = 'BEP20' # какой токен выводим

    amount_from = 10 # от какого кол-ва монет выводим
    amount_to   = 15 # до какого кол-ва монет выводим

    is_private_key = False # True если в wallets.txt вставил evm приватники. False если адреса (evm / не evm)

class Value_OKX():

    '''
    OKX
    BSC
    ERC20
    TRC20
    Polygon
    Avalanche C-Chain
    Avalanche X-Chain
    Arbitrum One
    Optimism
    Fantom
    zkSync Era
    StarkNet
    '''

    chain       = 'Polygon'
    symbol      = 'MATIC'

    amount_from = 1
    amount_to   = 2

    account = 'yanashulman'

    fee         = 0.1 # комса на вывод
    sub_acc     = False # True / False. True если хочешь проверять субаккаунты и сначала делать с них перевод на основной счет

    is_private_key = False # True если в wallets.txt вставил evm приватники. False если адреса (evm / не evm)

class Value_Transfer():

    '''
    вывод (трансфер) монет с кошельков
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync | celo | gnosis | core | harmony | base | linea
    '''

    chain                = 'bsc' # в какой сети выводить
    token_address        = '0x55d398326f99059ff775485246999027b3197955' # пусто если нативный токен сети

    amount_from          = 1 # от какого кол-ва монет делаем трансфер
    amount_to            = 2 # до какого кол-ва монет делаем трансфер  

    transfer_all_balance = False # True / False. если True, тогда выводим весь баланс
    min_amount_transfer  = 0 # если баланс будет меньше этого числа, выводить не будет
    keep_value_from      = 0 # от скольки монет оставляем на кошельке (работает только при : transfer_all_balance = True)
    keep_value_to        = 0 # до скольки монет оставляем на кошельке (работает только при : transfer_all_balance = True)
    
class Value_0x_Swap():

    '''
    свапы через апи 0x (агрегатор)
    docs : https://0x.org/docs/introduction/0x-cheat-sheet
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | celo
    '''

    chain               = 'bsc' # в какой сети свапаем
    from_token_address  = [''] # пусто если нативный токен сети
    to_token_address    = ['0x55d398326f99059ff775485246999027b3197955'] # пусто если нативный токен сети

    amount_from         = 0.0001 # от какого кол-ва монет свапаем
    amount_to           = 0.0002 # до какого кол-ва монет свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    slippage = 3 # слиппейдж, дефолт от 1 до 3

class Value_Orbiter():

    '''
    бридж нативных токенов через https://www.orbiter.finance/
    chains : zksync | ethereum | bsc | arbitrum | optimism | polygon_zkevm | nova | starknet | linea | base
    минимальный бридж : 0.005
    '''

    from_chain          = ['arbitrum'] # с какой сети 
    to_chain            = ['linea'] # в какую сеть 

    amount_from         = 0.006 # от какого кол-ва монет делаем бридж
    amount_to           = 0.0065 # до какого кол-ва монет делаем бридж

    bridge_all_balance  = False # True / False. если True, тогда бриджим весь баланс
    min_amount_bridge   = 0 # если баланс будет меньше этого числа, выводить не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)

class Value_Woofi_Bridge():

    '''
    бридж на https://fi.woo.org/ (бриджи идут через layerzero)
    chains : avalanche | polygon | ethereum | bsc | arbitrum | optimism | fantom
    '''
    
    from_chain          = 'bsc'
    to_chain            = 'polygon'

    from_token          = '' # пусто если нативный токен сети
    to_token            = '' # пусто если нативный токен сети

    amount_from         = 0.0001 # от какого кол-ва from_token свапаем
    amount_to           = 0.0002 # до какого кол-ва from_token свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

class Value_Woofi_Swap():

    '''
    свап на https://fi.woo.org/ 
    chains : avalanche | polygon | ethereum | bsc | arbitrum | optimism | fantom | zksync
    '''
    
    chain = 'arbitrum'

    from_token          = '0x6694340fc020c5e6b96567843da2df01b2ce1eb6' # пусто если нативный токен сети
    to_token            = '' # пусто если нативный токен сети

    amount_from         = 0.01 # от какого кол-ва from_token свапаем
    amount_to           = 0.1 # до какого кол-ва from_token свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

class Value_Sushiswap():

    '''
    внимание! большие сайзы лучше свапать через 1inch или 0x

    свап на https://www.sushi.com/swap
    chains :  arbitrum | nova | bsc | polygon | fantom
    '''
    
    chain = 'nova'

    from_token          = [''] # пусто если нативный токен сети
    to_token            = ['0x750ba8b76187092B0D1E87E28daaf484d1b5273b'] # пусто если нативный токен сети

    amount_from         = 1 # от какого кол-ва from_token свапаем
    amount_to           = 1 # до какого кол-ва from_token свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    slippage = 5 # советую ставить 1-5. если ошибка INSUFFICIENT_OUTPUT_AMOUNT , тогда увеличивай slippage

class Value_Bungee():

    '''
    refuel нативных токенов через https://www.bungee.exchange/
    chains : zksync | polygon | ethereum | bsc | arbitrum | optimism | fantom | polygon_zkevm | avalanche | gnosis
    '''

    from_chain          = ['arbitrum'] # с какой сети 
    to_chain            = ['polygon_zkevm'] # в какую сеть 

    amount_from         = 0.001 # от какого кол-ва монет делаем бридж
    amount_to           = 0.0015 # до какого кол-ва монет делаем бридж

    bridge_all_balance  = False # True / False. если True, тогда бриджим весь баланс
    min_amount_bridge   = 1 # если баланс будет меньше этого числа, выводить не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : bridge_all_balance = True)

class Value_Txn_Checker():

    '''
    чекер кол-ва транзакций (nonce) в каждой сети.
    1. если nonce < заданного числа, кошелек выделяется.
    2. закомментируй сеть, чтобы отключить ее.
    '''

    chains = {
        'ethereum'      : 10,
        'optimism'      : 0,
        'bsc'           : 5,
        'polygon'       : 0,
        'polygon_zkevm' : 0,
        'arbitrum'      : 0,
        'avalanche'     : 0,
        'fantom'        : 0,
        'nova'          : 20,
        'zksync'        : 15,
        'celo'          : 0,
        'gnosis'        : 0,
        'core'          : 0,
        'harmony'       : 1,
    }

class Value_1inch_Swap():

    '''
    свапы через 1inch
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | zksync
    '''

    chain               = 'bsc' # в какой сети свапаем
    from_token_address  = [''] # пусто если нативный токен сети
    to_token_address    = ['0x55d398326f99059ff775485246999027b3197955'] # пусто если нативный токен сети

    amount_from         = 0.0001 # от какого кол-ва монет свапаем
    amount_to           = 0.0002 # до какого кол-ва монет свапаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    slippage = 1 # слиппейдж, дефолт от 1 до 3

class Value_Merkly_Refuel():

    '''
    gas refuel через https://minter.merkly.com/gas
    внимание! сначала посмотри максималку руками, только потом запускай скрипт, иначе можешь потерять свои $.

    from_chains : optimism | bsc | polygon | arbitrum | avalanche | fantom | celo | zksync | polygon_zkevm | nova | harmony | gnosis | core
    to_chains   : avalanche | ethereum | bsc | arbitrum | optimism | fantom | harmony | celo | moonbeam | fuse | gnosis | klaytn | metis | core | polygon_zkevm | canto | zksync | moonriver | tenet | nova | kava | meter
    '''

    from_chain = ['polygon'] # сети, с которых хочешь делать refuel (>= 1 сети)
    to_chain   = ['kava', 'nova', 'tenet', 'moonriver', 'moonbeam'] # сети, на которые хочешь делать refuel (>= 1 сети)

    amount_from         = 0.000001 # от какого кол-ва нативного токена сети to_chain получаем
    amount_to           = 0.00001 # до какого кол-ва нативного токена сети to_chain получаем

    swap_all_balance    = False # True / False. если True, тогда свапаем весь баланс
    min_amount_swap     = 0 # если баланс будет меньше этого числа, свапать не будет
    keep_value_from     = 0 # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to       = 0 # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    get_layerzero_fee   = False # True если хочешь посмотреть газ. False если хочешь делать refuel
    
class Value_NFT_Checker():

    '''
    чекер nft
    chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync | polygon_zkevm | celo | gnosis | core | harmony | linea | base
    '''

    chain       = 'bsc'
    contract    = '0x6848dbcb498b32675a83e88841facfcd43ef8e32' # nft contract
    min_balance = 1 # если баланс nft меньше этого числа, кошелек выделяется
