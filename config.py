import asyncio
from modules.utils.files import read_txt, load_json
from modules.utils.helpers import get_chain_prices, get_wallet_proxies, get_bungee_data

max_time_check_tx_status = 100  # seconds. If a transaction does not return a status within this time, it is considered executed

# Which networks to enable in DeBank
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
    # },
    {
        "base": "BASE"
    },
]

STR_DONE = '✅ '
STR_CANCEL = '❌ '

ERC20_ABI = load_json("modules/utils/contracts/erc20.json")
MULTICALL_ABI = load_json("modules/utils/contracts/multicall_abi.json")
WALLETS = read_txt("datas/wallets.txt")
RECIPIENTS = read_txt("datas/recipients.txt")
STARKNET_ADDRESS = read_txt("datas/starknet_address.txt")
PROXIES = read_txt("datas/proxies.txt")
ORBITER_MAKER = load_json("modules/utils/contracts/orbiter_maker.json") # https://github.com/Orbiter-Finance/OrbiterFE-V2/tree/main/src/config (maker-1 / maker-2)
ABI_ZERIUS_REFUEL = load_json("modules/utils/contracts/zerius_refuel.json")

RECIPIENTS_WALLETS = dict(zip(WALLETS, RECIPIENTS))
STARKNET_WALLETS = dict(zip(WALLETS, STARKNET_ADDRESS))

WALLET_PROXIES = get_wallet_proxies(WALLETS, PROXIES)
PRICES_NATIVE = asyncio.run(get_chain_prices())
BUNGEE_LIMITS = asyncio.run(get_bungee_data())