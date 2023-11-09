TG_TOKEN = 'your_tgbot_token' # You can create one here: https://t.me/BotFather
TG_ID = 0 # You can find your Telegram User ID here: https://t.me/getmyid_bot

API_0x = 'your_0x_api_key' # Get your API key from 0x here: https://dashboard.0x.org/apps
API_1inch = 'your_0x_api_key' # Get your API key from 1inch here: https://portal.1inch.dev/login

# Replace RPC endpoints with your own
DATA = {
    "ethereum": {
        "rpc": "https://rpc.ankr.com/eth",
        "scan": "https://etherscan.io/tx",
        "token": "ETH",
        "chain_id": 1
    },
    "optimism": {
        "rpc": "https://rpc.ankr.com/optimism",
        "scan": "https://optimistic.etherscan.io/tx",
        "token": "ETH",
        "chain_id": 10
    },
    "bsc": {
        "rpc": "https://rpc.ankr.com/bsc",
        "scan": "https://bscscan.com/tx",
        "token": "BNB",
        "chain_id": 56
    },
    "polygon": {
        "rpc": "https://rpc.ankr.com/polygon",
        "scan": "https://polygonscan.com/tx",
        "token": "MATIC",
        "chain_id": 137
    },
    "polygon_zkevm": {
        "rpc": "https://zkevm-rpc.com",
        "scan": "https://zkevm.polygonscan.com/tx",
        "token": "ETH",
        "chain_id": 1101
    },
    "arbitrum": {
        "rpc": "https://rpc.ankr.com/arbitrum",
        "scan": "https://arbiscan.io/tx",
        "token": "ETH",
        "chain_id": 42161
    },
    "avalanche": {
        "rpc": "https://rpc.ankr.com/avalanche",
        "scan": "https://snowtrace.io/tx",
        "token": "AVAX",
        "chain_id": 43114
    },
    "fantom": {
        "rpc": "https://rpc.ankr.com/fantom",
        "scan": "https://ftmscan.com/tx",
        "token": "FTM",
        "chain_id": 250
    },
    "nova": {
        "rpc": "https://nova.arbitrum.io/rpc",
        "scan": "https://nova.arbiscan.io/tx",
        "token": "ETH",
        "chain_id": 42170
    },
    "zksync": {
        "rpc": "https://mainnet.era.zksync.io",
        "scan": "https://explorer.zksync.io/tx",
        "token": "ETH",
        "chain_id": 324
    },
    "celo": {
        "rpc": "https://1rpc.io/celo",
        "scan": "https://celoscan.io/tx",
        "token": "CELO",
        "chain_id": 42220
    },
    "gnosis": {
        "rpc": "https://rpc.ankr.com/gnosis",
        "scan": "https://gnosisscan.io/tx",
        "token": "xDAI",
        "chain_id": 100
    },
    "core": {
        "rpc": "https://rpc.coredao.org",
        "scan": "https://scan.coredao.org/tx",
        "token": "CORE",
        "chain_id": 1116
    },
    "harmony": {
        "rpc": "https://api.harmony.one",
        "scan": "https://explorer.harmony.one/tx",
        "token": "ONE",
        "chain_id": 1666600000
    },
    "moonbeam": {
        "rpc": "https://rpc.ankr.com/moonbeam",
        "scan": "https://moonscan.io/tx",
        "token": "GLMR",
        "chain_id": 1284
    },
    "moonriver": {
        "rpc": "https://moonriver.public.blastapi.io",
        "scan": "https://moonriver.moonscan.io/tx",
        "token": "MOVR",
        "chain_id": 1285
    },
    "linea": {
        "rpc": "https://rpc.linea.build",
        "scan": "https://lineascan.build/tx",
        "token": "ETH",
        "chain_id": 59144
    },
    "base": {
        "rpc": "https://mainnet.base.org",
        "scan": "https://basescan.org/tx",
        "token": "ETH",
        "chain_id": 8453
    },
    "zora": {
        "rpc": "https://rpc.zora.energy",
        "scan": "https://zora.superscan.network/tx",
        "token": "ETH",
        "chain_id": 7777777
    },
    "scroll": {
        "rpc": "https://scroll.blockpi.network/v1/rpc/public",
        "scan": "https://scrollscan.com/tx",
        "token": "ETH",
        "chain_id": 534352
    },
    "metis": {
        "rpc": "https://metis-mainnet.public.blastapi.io",
        "scan": "https://andromeda-explorer.metis.io/tx",
        "token": "METIS",
        "chain_id": 1088
    },
    "canto": {
        "rpc": "https://canto.slingshot.finance",
        "scan": "https://cantoscan.com/tx",
        "token": "CANTO",
        "chain_id": 7700
    },
    "starknet": {
        "rpc": "https://starknet-mainnet.public.blastapi.io",
        "scan": "https://starkscan.co/tx",
        "token": "ETH",
        "chain_id": None
    }
}

# API keys for exchanges. You can skip this if you don't use exchanges.
CEX_KEYS = {
    'binance'   : {'api_key': 'your_api_key', 'api_secret': 'your_api_secret'},
    'mexc'      : {'api_key': 'your_api_key', 'api_secret': 'your_api_secret'},
    'kucoin'    : {'api_key': 'your_api_key', 'api_secret': 'your_api_secret', 'password': 'your_api_password'},
    'huobi'     : {'api_key': 'your_api_key', 'api_secret': 'your_api_secret'},
    'bybit'     : {'api_key': 'your_api_key', 'api_secret': 'your_api_secret'},
    'bitget'    : {'api_key': 'your_api_key', 'api_secret': 'your_api_secret', 'password': 'your_api_password'},
}

# You can add any number of OKX accounts in the following format. This allows you to avoid constantly entering data for new accounts and simply reference them by name.
OKX_KEYS = {
    'account_1' : {
        'api_key'   : 'your_api_key',
        'api_secret': 'your_api_secret',
        'password'  : 'your_api_password',
    },
    'account_2' : {
        'api_key'   : 'your_api_key',
        'api_secret': 'your_api_secret',
        'password'  : 'your_api_password',
    },
}