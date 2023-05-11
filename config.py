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
    
# меняем рпс на свои
DATA = {
    'ethereum'      : {'rpc': 'https://rpc.ankr.com/eth', 'scan': 'https://etherscan.io/tx', 'token': 'ETH'},

    'optimism'      : {'rpc': 'https://rpc.ankr.com/optimism', 'scan': 'https://optimistic.etherscan.io/tx', 'token': 'ETH'},

    'bsc'           : {'rpc': 'https://rpc.ankr.com/bsc', 'scan': 'https://bscscan.com/tx', 'token': 'BNB'},

    'polygon'       : {'rpc': 'https://rpc.ankr.com/polygon', 'scan': 'https://polygonscan.com/tx', 'token': 'MATIC'},

    'polygon_zkevm' : {'rpc': 'https://zkevm-rpc.com', 'scan': 'https://zkevm.polygonscan.com/tx', 'token': 'ETH'},

    'arbitrum'      : {'rpc': 'https://rpc.ankr.com/arbitrum', 'scan': 'https://arbiscan.io/tx', 'token': 'ETH'},

    'avalanche'     : {'rpc': 'https://rpc.ankr.com/avalanche', 'scan': 'https://snowtrace.io/tx', 'token': 'AVAX'},

    'fantom'        : {'rpc': 'https://rpc.ankr.com/fantom', 'scan': 'https://ftmscan.com/tx', 'token': 'FTM'},

    'nova'          : {'rpc': 'https://nova.arbitrum.io/rpc', 'scan': 'https://nova.arbiscan.io/tx', 'token': 'ETH'},

    'zksync'        : {'rpc': 'https://mainnet.era.zksync.io', 'scan': 'https://explorer.zksync.io/tx', 'token': 'ETH'},
}

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

def recipients_evm():
    try:
        wallets = {}
        zero = -1
        for evm in WALLETS:
            zero += 1
            wallets.update({evm : RECIPIENTS[zero]})

        return wallets
    except Exception as error:
        # cprint(f'recipients_evm() error : {error}', 'red')
        return {}

RECIPIENTS_WALLETS = recipients_evm()

def starknet_wallets():
    try:
        wallets = {}
        zero = -1
        for evm in WALLETS:
            zero += 1
            wallets.update({evm : STARKNET_ADDRESS[zero]})

        return wallets
    except Exception as error:
        # cprint(f'recipients_evm() error : {error}', 'red')
        return {}
    
STARKNET_WALLETS = starknet_wallets()


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

RUN_TEXT = random.choice(texts)
RUN_COLOR = random.choice(colors)


