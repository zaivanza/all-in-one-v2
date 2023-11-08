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
    'scroll'        : 0.000000000000009019,
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
    'scroll'        : '9019',
}

# contract with X network to starknet
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
    'base'      : 184,
    'zora'      : 195,
    'scroll'    : 214,
}

WOOFI_BRIDGE_CONTRACTS = {
    'avalanche'     : '0x51AF494f1B4d3f77835951FA827D66fc4A18Dae8',
    'polygon'       : '0xAA9c15cd603428cA8ddD45e933F8EfE3Afbcc173',
    'ethereum'      : '0x9D1A92e601db0901e69bd810029F2C14bCCA3128',
    'bsc'           : '0x81004C9b697857fD54E137075b51506c739EF439',
    'arbitrum'      : '0x4AB421de52b3112D02442b040dd3DC73e8Af63b5',
    'optimism'      : '0xbeae1b06949d033da628ba3e5af267c3e740494b',
    'fantom'        : '0x72dc7fa5eeb901a34173C874A7333c8d1b34bca9',
}

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

# what to bridge to woofi (usdc / usdt)
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
    'base'          : '0xe8c5b8488feafb5df316be73ede3bdc26571a773'
}

ZERIUS_REFUEL_CONTRACTS = {
    'optimism'      : '0x2076BDd52Af431ba0E5411b3dd9B5eeDa31BB9Eb',
    'bsc'           : '0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD',
    'arbitrum'      : '0x412aea168aDd34361aFEf6a2e3FC01928Fba1248',
    'polygon'       : '0x2ef766b59e4603250265EcC468cF38a6a00b84b3',
    'polygon_zkevm' : '0xBAf5C493a4c364cBD2CA83C355E75F0ff7042945',
    # 'zksync'        : '' # temp unavailable,
    'avalanche'     : '0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD',
    'gnosis'        : '0x1fe2c567169d39CCc5299727FfAC96362b2Ab90E',
    'fantom'        : '0xBFd3539e4e0b1B29e8b08d17f30F1291C837a18E',
    'nova'          : '0x3Fc5913D35105f338cEfcB3a7a0768c48E2Ade8E',
    'harmony'       : '0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD', # unavailable : need to convert it to a one-address
    'core'          : '0xB47D82aA70f839dC27a34573f135eD6dE6CED9A5',
    'celo'          : '0xFF21d5a3a8e3E8BA2576e967888Deea583ff02f8',
    'moonbeam'      : '0xb0bea3bB2d6EDDD2014952ABd744660bAeF9747d',
    'base'          : '0x9415AD63EdF2e0de7D8B9D8FeE4b939dd1e52F2C',
    'scroll'        : '0xB074f8D92b930D3415DA6bA80F6D38f69ee4B9cf',
    'zora'          : '0x1fe2c567169d39CCc5299727FfAC96362b2Ab90E',
    'linea'         : '0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD',
    'metis'         : '0x1b07F1f4F860e72c9367e718a30e38130114AD22',
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

EXCLUDED_LZ_PAIRS = [
    (195, 102), # zora => bsc
    (195, 106), # zora => avalanche
    (214, 195), # scroll => zora
    (214, 184), # scroll => base
    (165, 214), # zksync => scroll
    (165, 195), # zksync => zora
    (183, 195), # linea => zora
    (183, 214), # linea => scroll
    (175, 158), # nova => polygon_zkevm
    (175, 195), # nova => zora
    (175, 214), # nova => scroll
    (175, 183), # nova => linea
    (175, 153), # nova => core
    (175,  125), # nova => celo
    (175, 116), # nova => harmony
    (175, 145), # nova => gnosis
]
ZERIUS_SEND_GAS_LIMIT = {
    101: 300000,
    110: 650000,
    111: 300000,
    109: 300000,
    102: 300000,
    106: 300000,
    184: 300000,
    195: 300000,
    214: 300000,
    165: 1800000,
    175: 300000, # nova
    183: 300000, # linea
}
ZERIUS_MINT_GAS_LIMIT = {
    101: 170000,
    110: 350000,
    111: 170000,
    109: 170000,
    102: 170000,
    106: 170000,
    184: 170000,
    195: 170000,
    214: 170000,
    165: 1000000,
    175: 170000, # nova
    183: 170000, # linea
}
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd"

LZ_CHAIN_TO_TOKEN = {
    101: 'ETH',
    110: 'ETH',
    111: 'ETH',
    109: 'MATIC',
    102: 'BNB',
    106: 'AVAX',
    184: 'ETH',
    195: 'ETH',
    214: 'ETH',
    165: 'ETH',
    175: 'ETH', # nova
    183: 'ETH', # linea
}
ZERIUS_CONTRACTS = {
    'ethereum': '0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41', 
    'optimism': '0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41', 
    'bsc': '0x250c34D06857b9C0A036d44F86d2c1Abe514B3Da', 
    'polygon': '0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41', 
    'arbitrum': '0x250c34D06857b9C0A036d44F86d2c1Abe514B3Da', 
    'avalanche': '0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41', 
    'base': '0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41',
    'zora': '0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41',
    'scroll': '0xEB22C3e221080eAD305CAE5f37F0753970d973Cd',
    'zksync': '0x7dA50bD0fb3C2E868069d9271A2aeb7eD943c2D6',
    'linea': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
    'nova': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
    'metis': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
    'moonbeam': '0x4c5AeDA35d8F0F7b67d6EB547eAB1df75aA23Eaf',
    'polygon_zkevm': '0x4c5AeDA35d8F0F7b67d6EB547eAB1df75aA23Eaf',
    'core': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
    'celo': '0x4c5AeDA35d8F0F7b67d6EB547eAB1df75aA23Eaf',
    'harmony': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
    'canto': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
    'fantom': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
    'gnosis': '0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7',
}

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

arbitrum_bridge_contracts = {
    "arbitrum": "0x4Dbd4fc535Ac27206064B68FfCf827b0A60BAB3f",
    "nova": "0xc4448b71118c9071Bcb9734A0EAc55D18A153949"
}