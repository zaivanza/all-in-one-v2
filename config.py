import requests, json, time, ccxt
from ccxt import ExchangeError
from loguru import logger
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import asyncio, aiohttp
from termcolor import cprint
import random
import telebot
from tqdm import tqdm
import hmac, base64
import csv
from pyuseragents import random as random_useragent
from tabulate import tabulate
import math
import decimal

from setting import *
from data.abi.abi import *
from data.data import *

max_time_check_tx_status = 100 # в секундах. если транза не выдаст статус за это время, она будет считаться исполненной

outfile = ''
with open(f"{outfile}data/abi/erc20.json", "r") as file:
    ERC20_ABI = json.load(file)

with open(f"{outfile}data/abi/orbiter_maker.json", "r") as file:
    ORBITER_MAKER = json.load(file)

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
    'aptos'     : 108
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

# разбивка массива на части по кол-ву элементов
def func_chunks_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]

def get_wallet_proxies():
    try:
        result = {}
        for i in range(len(WALLETS)):
            result[WALLETS[i]] = PROXIES[i % len(PROXIES)]
        return result
    except: None

def get_prices():

    try:

        prices = {
                'ETH': 0, 'BNB': 0, 'AVAX': 0, 'MATIC': 0, 'FTM': 0, 'xDAI': 0
            }

        for symbol in prices:

            url =f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
            response = requests.get(url)

            try:
                result  = [response.json()]
                price   = result[0]['USDT']
                prices[symbol] = float(price)
            except Exception as error:
                logger.error(f'{error}. set price : 0')
                prices[symbol] = 0

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
                'polygon_zkevm' : prices['ETH'], 
            }

        return data
    
    except Exception as error:
        logger.error(f'{error}. Try again')
        time.sleep(1)
        return get_prices()
    
def get_bungee_data():
    url = "https://refuel.socket.tech/chains"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    
PRICES_NATIVE   = get_prices()
WALLET_PROXIES  = get_wallet_proxies()
BUNGEE_LIMITS   = get_bungee_data()


