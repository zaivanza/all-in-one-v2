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

MULTICALL_ETH_CONTRACTS = {
    'ethereum': '0xb1f8e55c7f64d203c1400b9d8555d050f94adf39',
    'arbitrum': '0x151E24A486D7258dd7C33Fb67E4bB01919B7B32c',
    'bsc': '0x2352c63A83f9Fd126af8676146721Fa00924d7e4',
    'polygon': '0x2352c63A83f9Fd126af8676146721Fa00924d7e4',
    'optimism': '0xB1c568e9C3E6bdaf755A60c7418C269eb11524FC',
    'avalanche': '0xD023D153a0DFa485130ECFdE2FAA7e612EF94818',
    'fantom': '0x07f697424ABe762bB808c109860c04eA488ff92B',
    'era': '0x875fb0451fb2787b1924edc1DE4083E5f63D99Df',
    'zksync': '0x875fb0451fb2787b1924edc1DE4083E5f63D99Df',
    'nova': '0x3008e6ad64a470c47f428e73214c2f1f4e79b72d',
    'zora': '0x6830d287fE1dab06ABe252911caD71F37a0514A3',
    'linea': '0x3008e6ad64a470c47f428e73214C2F1f4e79b72d',
    'base': '0x162708433f00dbc8624795f181ec1983e418ef11',
    'polygon_zkevm': '0x162708433F00DBC8624795F181EC1983E418EF11',
    'core': '0xdAd633A2Ff9fb3Ab5d7a8bcfd089593c503c11a2',
    'gnosis': '0xd08149E71671A284e3F99b371BaF29BB8eEA7387',
    'goerli': '0x8242cd33761782f02bf10b7329cea5faf17b2bea',
    'moonbeam': '0xf614056a46e293DD701B9eCeBa5df56B354b75f9',
    'moonriver': '0xDEAa846cca7FEc9e76C8e4D56A55A75bb0973888',
    'aurora': '0x100665685d533F65bdD0BD1d65ca6387FC4F4FDB',
    'tron': 'TN8RtFXeQZyFHGmH1iiSRm5r4CRz1yWkCf',
    'celo': '0x6830d287fE1dab06ABe252911caD71F37a0514A3',
    'harmony': '0x3008e6ad64a470c47f428e73214c2f1f4e79b72d'
}

MULTICALL_CONTRACTS = {
    "ethereum"      : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "optimism"      : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "bsc"           : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "polygon"       : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "polygon_zkevm" : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "arbitrum"      : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "avalanche"     : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "fantom"        : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "nova"          : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "zksync"        : "0xF9cda624FBC7e059355ce98a31693d299FACd963",
    "celo"          : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "gnosis"        : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "core"          : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "harmony"       : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "moonbeam"      : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "moonriver"     : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "linea"         : "0xcA11bde05977b3631167028862bE2a173976CA11",
    "base"          : "0xcA11bde05977b3631167028862bE2a173976CA11"
}

