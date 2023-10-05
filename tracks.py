'''
all_modules сделан для примера, как нужно оформлять каждый модуль
'''

all_modules = [
    {
        'module_name': 'wait_balance',
        'module_number': 0,
        'params': {
            'chain': 'arbitrum', # в какой сети ждем 
            'min_balance': 0.01, # когда баланс станет > этого числа, модуль будет выполнен
            'token': '', # адрес токена. пусто если нативный токен
        },
    },
    {
        'module_name': 'sleeping',
        'module_number': 0,
        'params': {
            'from'  : 10, # от скольки спим
            'to'    : 50, # до скольки спим
        },
    },
    {
        'module_name': 'exchange_withdraw',
        'module_number': 3,
        'params': {
            'cex': 'binance',
            'chain': 'ETH',
            'symbol': 'USDT',
            'amount_from': 10,
            'amount_to': 15.5,
            'is_private_key': False,
        },
    },
    {
        'module_name': 'okx_withdraw',
        'module_number': 4,
        'params': {
            'chain': 'Arbitrum One (Bridged)',
            'symbol': 'USDC',
            'amount_from': 100,
            'amount_to': 400,
            'account': 'account_1',
            'fee': 0.1,
            'sub_acc': True,
            'is_private_key': True,
        },
    },
    {
        'module_name': 'transfer',
        'module_number': 5,
        'params': {
            'chain': 'bsc',
            'token_address': '',
            'amount_from': 0.1,
            'amount_to': 0.2,
            'transfer_all_balance': False,
            'min_amount_transfer': 0.01,
            'keep_value_from': 0,
            'keep_value_to': 0,
        },
    },
    {
        'module_name': '0x_swap',
        'module_number': 6,
        'params': {
            'chain': 'bsc',
            'from_token_address': [''],
            'to_token_address': ['0x55d398326f99059ff775485246999027b3197955'],
            'amount_from': 0.1,
            'amount_to': 0.2,
            'swap_all_balance': False,
            'min_amount_swap': 0.01,
            'keep_value_from': 0,
            'keep_value_to': 0,
            'slippage': 1,
        },
    },
    {
        'module_name': 'orbiter_bridge',
        'module_number': 7,
        'params': {
            'from_chain': ['arbitrum'],
            'to_chain': ['optimism'],
            'amount_from': 0.1,
            'amount_to': 0.2,
            'bridge_all_balance': False,
            'min_amount_bridge': 0.01,
            'keep_value_from': 0,
            'keep_value_to': 0,
        },
    },
    {
        'module_name': 'woofi_bridge',
        'module_number': 8,
        'params': {
            'from_chain': 'bsc',
            'to_chain': 'avalanche',
            'from_token': '0x55d398326f99059fF775485246999027B3197955',
            'to_token': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
            'amount_from': 0,
            'amount_to': 0,
            'swap_all_balance': True,
            'min_amount_swap': 1,
            'keep_value_from': 0.001,
            'keep_value_to': 0.003,
        },
    },
    {
        'module_name': 'woofi_swap',
        'module_number': 9,
        'params': {
            'chain': 'avalanche',
            'from_token': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
            'to_token': '0x152b9d0FdC40C096757F570A51E494bd4b943E50',
            'amount_from': 0,
            'amount_to': 0,
            'swap_all_balance': True,
            'min_amount_swap': 1,
            'keep_value_from': 0,
            'keep_value_to': 0,
        },
    },
    {
        'module_name': 'sushiswap',
        'module_number': 10,
        'params': {
            'chain': 'bsc',
            'from_token_address': [''],
            'to_token_address': ['0x55d398326f99059ff775485246999027b3197955'],
            'amount_from': 0.1,
            'amount_to': 0.2,
            'swap_all_balance': False,
            'min_amount_swap': 0.01,
            'keep_value_from': 0,
            'keep_value_to': 0,
            'slippage': 1,
        },
    },
    {
        'module_name': 'bungee_refuel',
        'module_number': 11,
        'params': {
            'from_chain': ['arbitrum'],
            'to_chain': ['zksync'],
            'amount_from': 0.003,
            'amount_to': 0.0036,
            'bridge_all_balance': False,
            'min_amount_bridge': 0.001,
            'keep_value_from': 0,
            'keep_value_to': 0,
        },
    },
    {
        'module_name': '1inch_swap',
        'module_number': 13,
        'params': {
            'chain': 'bsc',
            'from_token_address': [''],
            'to_token_address': ['0x55d398326f99059ff775485246999027b3197955'],
            'amount_from': 0.1,
            'amount_to': 0.2,
            'swap_all_balance': False,
            'min_amount_swap': 0.01,
            'keep_value_from': 0,
            'keep_value_to': 0,
            'slippage': 1,
        },
    },
    {
        'module_name': 'merkly_refuel',
        'module_number': 14,
        'params': {
            'from_chain': ['polygon'],
            'to_chain': ['kava', 'nova', 'tenet', 'moonriver', 'moonbeam'],
            'amount_from': 0.0002,
            'amount_to': 0.003,
            'swap_all_balance': False,
            'min_amount_swap': 0,
            'keep_value_from': 0,
            'keep_value_to': 0,
            'get_layerzero_fee': False,
        },
    }
]

track_1 = [
    {
        'module_name': 'exchange_withdraw',
        'module_number': 3,
        'params': {
            'cex': 'binance',
            'chain': 'BEP20',
            'symbol': 'BNB',
            'amount_from': 0.2,
            'amount_to': 0.3,
            'is_private_key': False,
        },
    },
    {
        'module_name': 'wait_balance',
        'module_number': 0,
        'params': {
            'chain': 'bsc', # в какой сети ждем 
            'min_balance': 0.15, # когда баланс станет > этого числа, модуль будет выполнен
            'token': '', # адрес токена. пусто если нативный токен
        },
    },
    {
        'module_name': 'sleeping',
        'module_number': 0,
        'params': {
            'from'  : 20, # от скольки спим
            'to'    : 40, # до скольки спим
        },
    },
    {
        'module_name': 'woofi_bridge',
        'module_number': 8,
        'params': {
            'from_chain': 'bsc',
            'to_chain': 'arbitrum',
            'from_token': '',
            'to_token': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
            'amount_from': 0.1,
            'amount_to': 0.12,
            'swap_all_balance': False,
            'min_amount_swap': 0,
            'keep_value_from': 0,
            'keep_value_to': 0,
        },
    },
    {
        'module_name': 'wait_balance',
        'module_number': 0,
        'params': {
            'chain': 'arbitrum', # в какой сети ждем 
            'min_balance': 10, # когда баланс станет > этого числа, модуль будет выполнен
            'token': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', # адрес токена. пусто если нативный токен
        },
    },
    {
        'module_name': 'sleeping',
        'module_number': 0,
        'params': {
            'from'  : 10, # от скольки спим
            'to'    : 50, # до скольки спим
        },
    },
    {
        'module_name': 'transfer',
        'module_number': 5,
        'params': {
            'chain': 'arbitrum',
            'token_address': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
            'amount_from': 0,
            'amount_to': 0,
            'transfer_all_balance': True,
            'min_amount_transfer': 10,
            'keep_value_from': 0,
            'keep_value_to': 0,
        },
    },
]

