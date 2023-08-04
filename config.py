import json, time
import random, requests
from loguru import logger
from tqdm import tqdm
import asyncio, aiohttp

max_time_check_tx_status = 100 # в секундах. если транза не выдаст статус за это время, она будет считаться исполненной

outfile = ''
with open(f"{outfile}data/abi/erc20.json", "r") as file:
    ERC20_ABI = json.load(file)

with open(f"{outfile}data/abi/orbiter_maker.json", "r") as file:
    ORBITER_MAKER = json.load(file) # https://github.com/Orbiter-Finance/OrbiterFE-V2/tree/main/src/config

with open(f"{outfile}data/wallets.txt", "r") as f:
    WALLETS = [row.strip() for row in f]

with open(f"{outfile}data/recipients.txt", "r") as f:
    RECIPIENTS = [row.strip() for row in f]

with open(f"{outfile}data/starknet_address.txt", "r") as f:
    STARKNET_ADDRESS = [row.strip() for row in f]

with open(f"{outfile}data/proxies.txt", "r") as f:
    PROXIES = [row.strip() for row in f]


STR_DONE    = '✅ '
STR_CANCEL  = '❌ '

# какие сети активируем в дебанке
DEBANK_ACTIVATE_CHAINS = [
    {
        "eth": "Ethereum"
    },
    {
        "bsc": "BNB Chain"
    },
    {
        "xdai": "Gnosis Chain"
    },
    # {
    #     "heco": "HECO"
    # },
    {
        "matic": "Polygon"
    },
    {
        "ftm": "Fantom"
    },
    # {
    #     "okt": "OKC"
    # },
    {
        "avax": "Avalanche"
    },
    {
        "op": "Optimism"
    },
    {
        "arb": "Arbitrum"
    },
    # {
    #     "celo": "Celo"
    # },
    # {
    #     "movr": "Moonriver"
    # },
    # {
    #     "cro": "Cronos"
    # },
    # {
    #     "boba": "Boba"
    # },
    # {
    #     "metis": "Metis"
    # },
    # {
    #     "btt": "BitTorrent"
    # },
    # {
    #     "aurora": "Aurora"
    # },
    # {
    #     "mobm": "Moonbeam"
    # },
    # {
    #     "sbch": "SmartBch"
    # },
    # {
    #     "fuse": "Fuse"
    # },
    {
        "hmy": "Harmony"
    },
    # {
    #     "klay": "Klaytn"
    # },
    # {
    #     "astar": "Astar"
    # },
    # {
    #     "palm": "Palm"
    # },
    # {
    #     "sdn": "Shiden"
    # },
    # {
    #     "iotx": "IoTeX"
    # },
    # {
    #     "rsk": "RSK"
    # },
    # {
    #     "wan": "Wanchain"
    # },
    # {
    #     "kcc": "KCC"
    # },
    # {
    #     "sgb": "Songbird"
    # },
    # {
    #     "evmos": "EvmOS"
    # },
    # {
    #     "dfk": "DFK"
    # },
    # {
    #     "tlos": "Telos"
    # },
    # {
    #     "swm": "Swimmer"
    # },
    {
        "nova": "Arbitrum Nova"
    },
    # {
    #     "canto": "Canto"
    # },
    # {
    #     "doge": "Dogechain"
    # },
    # {
    #     "kava": "Kava"
    # },
    # {
    #     "step": "Step"
    # },
    # {
    #     "cfx": "Conflux"
    # },
    # {
    #     "mada": "Milkomeda"
    # },
    # {
    #     "brise": "Bitgert"
    # },
    # {
    #     "ckb": "Godwoken"
    # },
    # {
    #     "tomb": "TOMB Chain"
    # },
    {
        "era": "zkSync Era"
    },
    # {
    #     "ron": "Ronin"
    # },
    {
        "pze": "Polygon zkEVM"
    },
    # {
    #     "eos": "EOS EVM"
    # },
    {
        "core": "CORE"
    },
    # {
    #     "wemix": "WEMIX"
    # },
    # {
    #     "etc": "Ethereum Classic"
    # },
    # {
    #     "pls": "Pulse"
    # },
    # {
    #     "flr": "Flare"
    # },
    # {
    #     "fsn": "Fusion"
    # },
    # {
    #     "mtr": "Meter"
    # },
    # {
    #     "rose": "Oasis Emerald"
    # }
]


def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def decimalToInt(qty, decimal):
    return qty/ int("".join((["1"]+ ["0"]*decimal)))

def call_json(result, outfile):
    with open(f"{outfile}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

RECIPIENTS_WALLETS  = dict(zip(WALLETS, RECIPIENTS))
STARKNET_WALLETS    = dict(zip(WALLETS, STARKNET_ADDRESS))

ORBITER_AMOUNT = {
    'ethereum'      : 0.000000000000009001,
    'optimism'      : 0.000000000000009007,
    'bsc'           : 0.000000000000009015,
    'arbitrum'      : 0.000000000000009002,
    'nova'          : 0.000000000000009016,
    'polygon'       : 0.000000000000009006,
    'polygon_zkevm' : 0.000000000000009017,
    'zksync'        : 0.000000000000009014,
    'zksync_lite'   : 0.000000000000009003,
    'starknet'      : 0.000000000000009004,
    'linea'         : 0.000000000000009023,
    'base'          : 0.000000000000009021,
    'mantle'        : 0.000000000000009024,
}

ORBITER_AMOUNT_STR = {
    'ethereum'      : '9001',
    'optimism'      : '9007',
    'bsc'           : '9015',
    'arbitrum'      : '9002',
    'nova'          : '9016',
    'polygon'       : '9006',
    'polygon_zkevm' : '9017',
    'zksync'        : '9014',
    'zksync_lite'   : '9003',
    'starknet'      : '9004',
    'linea'         : '9023',
    'base'          : '9021',
    'mantle'        : '9024',
}

# контракт с X сети в starknet
CONTRACTS_ORBITER_TO_STARKNET = {
    'ethereum'      : '0xd9d74a29307cc6fc8bf424ee4217f1a587fbc8dc',
    'optimism'      : '',
    'bsc'           : '',
    'arbitrum'      : '0xd9d74a29307cc6fc8bf424ee4217f1a587fbc8dc',
    'nova'          : '',
    'polygon'       : '',
    'polygon_zkevm' : '',
    'zksync'        : '',
    'zksync_lite'   : '',
}

LAYERZERO_CHAINS_ID = {
    'avalanche' : 106,
    'polygon'   : 109,
    'ethereum'  : 101,
    'bsc'       : 102,
    'arbitrum'  : 110,
    'optimism'  : 111,
    'fantom'    : 112,
    'aptos'     : 108,
    'harmony'   : 116,
    'celo'      : 125,
    'moonbeam'  : 126,
    'fuse'      : 138,
    'gnosis'    : 145,
    'klaytn'    : 150,
    'metis'     : 151,
    'core'      : 153,
    'polygon_zkevm': 158,
    'canto'     : 159,
    'zksync'    : 165,
    'moonriver' : 167,
    'tenet'     : 173,
    'nova'      : 175,
    'kava'      : 177,
    'meter'     : 176,
}

# контракты бриджа
WOOFI_BRIDGE_CONTRACTS = {
    'avalanche'     : '0x51AF494f1B4d3f77835951FA827D66fc4A18Dae8',
    'polygon'       : '0xAA9c15cd603428cA8ddD45e933F8EfE3Afbcc173',
    'ethereum'      : '0x9D1A92e601db0901e69bd810029F2C14bCCA3128',
    'bsc'           : '0x81004C9b697857fD54E137075b51506c739EF439',
    'arbitrum'      : '0x4AB421de52b3112D02442b040dd3DC73e8Af63b5',
    'optimism'      : '0xbeae1b06949d033da628ba3e5af267c3e740494b',
    'fantom'        : '0x72dc7fa5eeb901a34173C874A7333c8d1b34bca9',
}

# контракты свапа
WOOFI_SWAP_CONTRACTS = {
    'avalanche'     : '0xC22FBb3133dF781E6C25ea6acebe2D2Bb8CeA2f9',
    'polygon'       : '0x817Eb46D60762442Da3D931Ff51a30334CA39B74',
    'ethereum'      : '',
    'bsc'           : '0x4f4Fd4290c9bB49764701803AF6445c5b03E8f06',
    'arbitrum'      : '0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
    'optimism'      : '0xEAf1Ac8E89EA0aE13E0f03634A4FF23502527024',
    'fantom'        : '0x382A9b0bC5D29e96c3a0b81cE9c64d6C8F150Efb',
    'zksync'        : '0xfd505702b37Ae9b626952Eb2DD736d9045876417',
}

# через что бриджим на woofi (usdc / usdt)
WOOFI_PATH = {
    'avalanche'     : '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
    'polygon'       : '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
    'ethereum'      : '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    'bsc'           : '0x55d398326f99059ff775485246999027b3197955',
    'arbitrum'      : '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
    'optimism'      : '0x7f5c764cbc14f9669b88837ca1490cca17c31607',
    'fantom'        : '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
}

WETH_CONTRACTS = {
    'ethereum'      : '',
    'optimism'      : '0x4200000000000000000000000000000000000006',
    'bsc'           : '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', # WBNB
    'arbitrum'      : '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
    'nova'          : '0x722E8BdD2ce80A4422E880164f2079488e115365', # WETH
    'polygon'       : '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270', # WMATIC
    'polygon_zkevm' : '',
    'fantom'        : '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83',
    'zksync'        : '',
    'zksync_lite'   : '',
    'starknet'      : '',
}

SUSHISWAP_CONTRACTS = {
    'ethereum'      : '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
    'optimism'      : '0x4C5D5234f232BD2D76B96aA33F5AE4FCF0E4BFAb',
    'bsc'           : '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
    'arbitrum'      : '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
    'nova'          : '0x1b02da8cb0d097eb8d57a175b88c7d8b47997506',
    'polygon'       : '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
    'polygon_zkevm' : '',
    'fantom'        : '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
    'zksync'        : '',
    'zksync_lite'   : '',
    'starknet'      : '',
}

BUNGEE_REFUEL_CONTRACTS = {
    'ethereum'      : '0xb584D4bE1A5470CA1a8778E9B86c81e165204599',
    'optimism'      : '0x5800249621da520adfdca16da20d8a5fc0f814d8',
    'bsc'           : '0xbe51d38547992293c89cc589105784ab60b004a9',
    'arbitrum'      : '0xc0e02aa55d10e38855e13b64a8e1387a04681a00',
    'polygon'       : '0xAC313d7491910516E06FBfC2A0b5BB49bb072D91',
    'polygon_zkevm' : '0x555a64968e4803e27669d64e349ef3d18fca0895',
    'zksync'        : '0x7Ee459D7fDe8b4a3C22b9c8C7aa52AbadDd9fFD5',
    'avalanche'     : '0x040993fbf458b95871cd2d73ee2e09f4af6d56bb',
    'gnosis'        : '0xBE51D38547992293c89CC589105784ab60b004A9',
    'fantom'        : '0x040993fbF458b95871Cd2D73Ee2E09F4AF6d56bB',
}

MERKLY_CONTRACTS = {
    'optimism'      : '0xa2c203d7ef78ed80810da8404090f926d67cd892',
    'bsc'           : '0xfdc9018af0e37abf89233554c937eb5068127080',
    'arbitrum'      : '0xaa58e77238f0e4a565343a89a79b4addd744d649',
    'polygon'       : '0xa184998ec58dc1da77a1f9f1e361541257a50cf4',
    # 'polygon_zkevm' : '', пока недоступен
    'zksync'        : '0x6dd28C2c5B91DD63b4d4E78EcAC7139878371768',
    'avalanche'     : '0xe030543b943bdcd6559711ec8d344389c66e1d56',
    'gnosis'        : '0xb58f5110855fbef7a715d325d60543e7d4c18143',
    'fantom'        : '0x97337a9710beb17b8d77ca9175defba5e9afe62e',
    'nova'          : '0x484c402b0c8254bd555b68827239bace7f491023',
    # 'harmony'       : '', # надо конвертировать в one-address
    'core'          : '0xCA230856343C300f0cc2Bd77C89F0fCBeDc45B0f',
    'celo'          : '0xe33519c400b8f040e73aeda2f45dfdd4634a7ca0',
    'moonbeam'      : '0x766b7aC73b0B33fc282BdE1929db023da1fe6458',
    'moonriver'     : '0x97337A9710BEB17b8D77cA9175dEFBA5e9AFE62e',
}

text1 = '''
 /$$   /$$  /$$$$$$  /$$$$$$$  /$$       /$$      /$$  /$$$$$$  /$$$$$$$ 
| $$  | $$ /$$__  $$| $$__  $$| $$      | $$$    /$$$ /$$__  $$| $$__  $$
| $$  | $$| $$  \ $$| $$  \ $$| $$      | $$$$  /$$$$| $$  \ $$| $$  \ $$
| $$$$$$$$| $$  | $$| $$  | $$| $$      | $$ $$/$$ $$| $$  | $$| $$  | $$
| $$__  $$| $$  | $$| $$  | $$| $$      | $$  $$$| $$| $$  | $$| $$  | $$
| $$  | $$| $$  | $$| $$  | $$| $$      | $$\  $ | $$| $$  | $$| $$  | $$
| $$  | $$|  $$$$$$/| $$$$$$$/| $$$$$$$$| $$ \/  | $$|  $$$$$$/| $$$$$$$/
|__/  |__/ \______/ |_______/ |________/|__/     |__/ \______/ |_______/                                                                                                                                                                                                          
'''

text2 = '''
      ___          ___                                    ___          ___                  
     /\  \        /\  \        _____                     /\  \        /\  \        _____    
     \:\  \      /::\  \      /::\  \                   |::\  \      /::\  \      /::\  \   
      \:\  \    /:/\:\  \    /:/\:\  \                  |:|:\  \    /:/\:\  \    /:/\:\  \  
  ___ /::\  \  /:/  \:\  \  /:/  \:\__\  ___     ___  __|:|\:\  \  /:/  \:\  \  /:/  \:\__\ 
 /\  /:/\:\__\/:/__/ \:\__\/:/__/ \:|__|/\  \   /\__\/::::|_\:\__\/:/__/ \:\__\/:/__/ \:|__|
 \:\/:/  \/__/\:\  \ /:/  /\:\  \ /:/  /\:\  \ /:/  /\:\~~\  \/__/\:\  \ /:/  /\:\  \ /:/  /
  \::/__/      \:\  /:/  /  \:\  /:/  /  \:\  /:/  /  \:\  \       \:\  /:/  /  \:\  /:/  / 
   \:\  \       \:\/:/  /    \:\/:/  /    \:\/:/  /    \:\  \       \:\/:/  /    \:\/:/  /  
    \:\__\       \::/  /      \::/  /      \::/  /      \:\__\       \::/  /      \::/  /   
     \/__/        \/__/        \/__/        \/__/        \/__/        \/__/        \/__/    
'''

texts = [text1, text2]
colors = ['green', 'yellow', 'blue', 'magenta', 'cyan']

RUN_TEXT    = random.choice(texts)
RUN_COLOR   = random.choice(colors)

def get_wallet_proxies(wallets, proxies):
    try:
        result = {}
        for i in range(len(wallets)):
            result[wallets[i]] = proxies[i % len(proxies)]
        return result
    except: None

async def get_prices():

    prices = {
                'ETH': 0, 'BNB': 0, 'AVAX': 0, 'MATIC': 0, 'FTM': 0, 'xDAI': 0, 'CELO': 0, 'COREDAO': 0, 'ONE': 0, 'MOVR': 0, 'GLMR': 0
            }

    async def get_get(session, symbol):

        url =f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'

        async with session.get(url, timeout=10) as resp:

            try:

                if resp.status == 200:
                    resp_json = await resp.json(content_type=None)
                    
                    try:
                        prices[symbol] = float(resp_json['USDT'])
                    except Exception as error:
                        logger.error(f'{error}. set price : 0')
                        prices[symbol] = 0

                else:
                    await asyncio.sleep(1)
                    return await get_get(session, url)

            except Exception as error:
                await asyncio.sleep(1)
                return await get_get(session, url)

    async with aiohttp.ClientSession() as session:

        tasks = []
            
        for symbol in prices:
            task = asyncio.create_task(get_get(session, symbol))
            tasks.append(task)

        await asyncio.gather(*tasks)

    data = {
            'avalanche'     : prices['AVAX'], 
            'polygon'       : prices['MATIC'], 
            'ethereum'      : prices['ETH'], 
            'bsc'           : prices['BNB'], 
            'arbitrum'      : prices['ETH'], 
            'optimism'      : prices['ETH'], 
            'fantom'        : prices['FTM'], 
            'zksync'        : prices['ETH'], 
            'nova'          : prices['ETH'], 
            'gnosis'        : prices['xDAI'], 
            'celo'          : prices['CELO'], 
            'polygon_zkevm' : prices['ETH'], 
            'core'          : prices['COREDAO'], 
            'harmony'       : prices['ONE'], 
            'moonbeam'      : prices['GLMR'], 
            'moonriver'     : prices['MOVR'], 
            'linea'         : prices['ETH'], 
            'base'          : prices['ETH'], 
        }

    return data
    
def get_bungee_data():
    url = "https://refuel.socket.tech/chains"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    

PRICES_NATIVE   = asyncio.run(get_prices())
WALLET_PROXIES  = get_wallet_proxies(WALLETS, PROXIES)
BUNGEE_LIMITS   = get_bungee_data()


