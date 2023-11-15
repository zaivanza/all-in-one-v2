from tracks import *

# --- Settings ---
WALLETS_IN_BATCH = 1    # How many wallets to run in one thread (simultaneously)

USE_TRACKS = False      # Enable/disable tracks
TRACK = track_1         # Change to the track variable from routes.py

IS_SLEEP = True         # Enable/disable delay between wallets
DELAY_SLEEP = [10, 30]  # Delay range between wallets (seconds)
RANDOMIZER = False      # Enable/disable random wallet shuffling
RETRY = 0               # Number of retries on errors/failures
TG_BOT_SEND = True      # Enable/disable sending results to a Telegram bot

USE_PROXY = False       # Enable/disable proxy usage in web3 requests
CHECK_GWEI = True       # Enable/disable base Gwei checking
MAX_GWEI = 30           # Maximum Gwei (see https://etherscan.io/gastracker)

# Maximum transaction fee in USD, at which the script will sleep for 30 seconds and retry
MAX_GAS_CHARGE = {
    'avalanche'     : 1,
    'polygon'       : 0.5,
    'ethereum'      : 7,
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
    'base'          : 0.5,
    'scroll'        : 0.5,
    'zora'          : 0.5,
    'moonbeam'      : 0.5,
    'moonriver'     : 0.5,
    'canto'         : 0.5,
    'metis'         : 0.5,
    'linea'         : 0.5,
}

class Value_EVM_Balance_Checker:

    '''
    Coins checker
    Chains : ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync | polygon_zkevm | celo | gnosis | core | harmony | linea | base
    '''

    # Comment out the chain / token if you do not want to check the balance of that chain / token
    evm_tokens = {
        'bsc': [
            '', # BNB
            '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d', # USDC
            '0x55d398326f99059ff775485246999027b3197955', # USDT
            '0xe9e7cea3dedca5984780bafc599bd69add087d56', # BUSD
            # '0xB0b84D294e0C75A6abe60171b70edEb2EFd14A1B', # SnBNB
            ],
        'arbitrum': [
            '', # ETH
            '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', # USDT
            '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', # USDC
            # '0x6694340fc020c5e6b96567843da2df01b2ce1eb6', # STG
            '0x912ce59144191c1204e64559fe8253a0e49e6548', # ARB
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
        'fantom': [
            '', # FTM
            ],
        'polygon_zkevm': [
            '', # ETH
            ],
        # 'celo': [
        #     '', # CELO
        #     ],
        'gnosis': [
            '', # xDAI
            ],
        'harmony': [
            '', # ONE
            ],
        'core': [
            '', # CORE
            ],
        'linea': [
            '', # ETH
            ],
        'base': [
            '', # ETH
            ],
    }

    min_token_balance = {
        'chain'     : 'bsc',
        'coin'      : 'BNB',
        'amount'    : 0 # If the balance is less than this amount, the wallet will be highlighted
    }

    min_value_balance = 5 # If the wallet balance in $ is less than this amount, the wallet will be highlighted    
    
class Value_Starknet_Balance_Checker:
    '''
    Starknet Balance Checker
    '''

    # Comment out the token if you do not want to check the balance of that token
    starknet_tokens = [
        "ETH", 
        # "USDC",
        # "USDT",
        # "DAI",
        # "WBTC",
    ]
    
    min_token_balance = {
        'symbol': 'ETH',
        'amount': 0.005 # If the balance is less than this amount, the wallet will be highlighted
    }

    min_value_balance = 15 # If the wallet balance in $ is less than this amount, the wallet will be highlighted    
    
class Value_DeBank:

    '''
    Balance checker using DeBank, which looks at all networks, protocols, and NFTs.

    If you haven't run this checker on your wallets before, you can activate them first by setting activate_wallets = True.
    The networks to activate are defined in config.py => DEBANK_ACTIVATE_CHAINS. I have commented out unnecessary networks. If needed, you can uncomment them.
    '''

    activate_wallets = True  # Set to True if you need to activate wallets (for the first run). Set to False to deactivate.

    # Enable/disable modules. If a module is not needed, comment it out (#). The NFT module is the slowest, so it's better to disable it if not needed.
    modules = [
        'token',    # Check tokens
        # 'nft',    # Check NFTs
        'protocol'  # Check protocols
    ]

    # Specify the networks to check for NFTs. If a network is not needed, comment it out (#).
    nft_chains = [
        'op', 
        'eth', 
        # 'arb', 
        # 'matic', 
        # 'bsc',
        'base'
    ]

    check_min_value = 1  # $. If the balance of a token / protocol is less than this amount, it won't be recorded in the file.
    check_chain = ''     # Network in which to look for the token (will highlight its balance separately).
    check_coin = ''      # Which coin to look for (will highlight its balance separately).

class Value_Exchange:

    '''
    Withdraw coins from an exchange.
    Exchanges: binance | bybit | kucoin | mexc | huobi | bitget

    Chains:
    - binance: ETH | BEP20 | AVAXC | MATIC | ARBITRUM | OPTIMISM | APT
    - bybit
    - kucoin
    - mexc
    - huobi
    - bitget: zkSyncEra | ArbitrumNova | ArbitrumOne | ETH / ERC20 | Optimism | BEP20 | TRC20 | Polygon | Aptos | CELO | CoreDAO | Harmony
    '''

    exchange    = 'binance' # Specify the exchange here

    chain       = 'APT' # In which network to withdraw
    symbol      = 'APT' # Which token to withdraw

    amount_from = 0.05 # Withdrawal from a certain amount of coins
    amount_to   = 0.05 # Withdrawal up to a certain amount of coins

    is_private_key = False # Set to True if you have inserted EVM private keys in wallets.txt. Set to False if you have addresses (EVM / non-EVM).

class Value_OKX:

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

    chain   = 'Polygon'
    symbol  = 'MATIC'

    amount_from = 1
    amount_to   = 2

    account = 'account_1'

    fee     = 0.1 # Withdrawal fee
    sub_acc = False # True / False. True if you want to check sub-accounts and first transfer from them to the main account

    is_private_key = False # Set to True if you have inserted EVM private keys in wallets.txt. Set to False if you have addresses (EVM / non-EVM).

class Value_Transfer:

    '''
    Withdraw (transfer) coins from wallets
    Chains: ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync | celo | gnosis | core | harmony | base | linea | polygon_zkevm
    '''

    chain                = 'polygon_zkevm' # Network to withdraw to
    token_address        = '' # Leave empty if it's the native token of the network

    amount_from          = 1 # Transfer from a certain amount of coins
    amount_to            = 2 # Transfer up to a certain amount of coins

    transfer_all_balance = False # True / False. If True, then transfer the entire balance
    min_amount_transfer  = 0 # If the balance is less than this amount, no transfer will be made
    keep_value_from      = 0 # How many coins to keep on the wallet (only works when: transfer_all_balance = True)
    keep_value_to        = 0 # Up to how many coins to keep on the wallet (only works when: transfer_all_balance = True)

class Value_0x_Swap:

    '''
    Swaps via the 0x API (aggregator)
    Docs: https://0x.org/docs/introduction/0x-cheat-sheet
    Chains: ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | celo
    '''

    chain               = 'bsc' # Network to perform swaps on
    from_token_address  = [''] # Leave empty if it's the native token of the network
    to_token_address    = ['0x55d398326f99059ff775485246999027b3197955'] # Leave empty if it's the native token of the network

    amount_from         = 0.0001 # Swap from a certain amount of coins
    amount_to           = 0.0002 # Swap up to a certain amount of coins

    swap_all_balance    = False # True / False. If True, then swap the entire balance
    min_amount_swap     = 0 # If the balance is less than this amount, no swap will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)

    slippage = 3 # Slippage, default is from 1 to 3

class Value_Orbiter:

    '''
    Bridge ETH via https://www.orbiter.finance/
    Chains: zksync | ethereum | bsc | arbitrum | optimism | polygon_zkevm | nova | starknet | linea | base | scroll
    Minimum bridge amount: 0.005
    '''

    from_chain          = ['arbitrum'] # From which network
    to_chain            = ['base'] # To which network

    amount_from         = 0.006 # Bridge from a certain amount of coins
    amount_to           = 0.008 # Bridge up to a certain amount of coins

    bridge_all_balance  = False # True / False. If True, then bridge the entire balance
    min_amount_bridge   = 0 # If the balance is less than this amount, no bridge will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)

class Value_Woofi_Bridge:

    '''
    Bridge on https://fi.woo.org/ (bridges go through layerzero)
    Chains: avalanche | polygon | ethereum | bsc | arbitrum | optimism | fantom
    '''

    from_chain          = 'bsc'
    to_chain            = 'polygon'

    from_token          = '' # Leave empty if it's the native token of the from_chain
    to_token            = '' # Leave empty if it's the native token of the to_chain

    amount_from         = 0.0001 # Swap from a certain amount of from_token
    amount_to           = 0.0002 # Swap up to a certain amount of from_token

    swap_all_balance    = False # True / False. If True, then swap the entire balance
    min_amount_swap     = 0 # If the balance is less than this amount, no swap will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)

class Value_Woofi_Swap:

    '''
    Swap on https://fi.woo.org/ 
    Chains: avalanche | polygon | ethereum | bsc | arbitrum | optimism | fantom | zksync
    '''

    chain = 'arbitrum'

    from_token          = '0x6694340fc020c5e6b96567843da2df01b2ce1eb6' # Leave empty if it's the native token of the chain
    to_token            = '' # Leave empty if it's the native token of the chain

    amount_from         = 0.01 # Swap from a certain amount of from_token
    amount_to           = 0.1 # Swap up to a certain amount of from_token

    swap_all_balance    = False # True / False. If True, then swap the entire balance
    min_amount_swap     = 0 # If the balance is less than this amount, no swap will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)

class Value_Sushiswap:

    '''
    Attention! It's better to swap large sizes through 1inch or 0x.

    Swap on https://www.sushi.com/swap
    Chains: arbitrum | nova | bsc | polygon | fantom
    '''
    
    chain = 'nova'

    from_token          = [''] # Leave empty if it's the native token of the chain
    to_token            = ['0x750ba8b76187092B0D1E87E28daaf484d1b5273b'] # Leave empty if it's the native token of the chain

    amount_from         = 1 # Swap from a certain amount of from_token
    amount_to           = 1 # Swap up to a certain amount of from_token

    swap_all_balance    = False # True / False. If True, then swap the entire balance
    min_amount_swap     = 0 # If the balance is less than this amount, no swap will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)

    slippage = 5 # I recommend setting it to 1-5. If you get the error INSUFFICIENT_OUTPUT_AMOUNT, then increase the slippage.

class Value_Bungee:

    '''
    Refuel native tokens via https://www.bungee.exchange/
    Chains: zksync | polygon | ethereum | bsc | arbitrum | optimism | fantom | polygon_zkevm | avalanche | gnosis | base
    '''

    from_chain          = ['base'] # From which network
    to_chain            = ['zksync'] # To which network

    amount_from         = 0.0013 # Refuel from a certain amount of coins
    amount_to           = 0.002 # Refuel up to a certain amount of coins

    bridge_all_balance  = False # True / False. If True, then refuel the entire balance
    min_amount_bridge   = 0 # If the balance is less than this amount, no refuel will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)

class Value_Txn_Checker:

    '''
    Transaction count (nonce) checker for each network.
    1. If nonce < the specified number, the wallet is flagged.
    2. Comment out a network to disable it.
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

class Value_1inch_Swap:

    '''
    Swaps via 1inch
    Chains: ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | zksync
    '''

    chain               = 'bsc' # Network to perform swaps on
    from_token_address  = [''] # Leave empty if it's the native token of the network
    to_token_address    = ['0x55d398326f99059ff775485246999027b3197955'] # Leave empty if it's the native token of the network

    amount_from         = 0.0001 # Swap from a certain amount of coins
    amount_to           = 0.0002 # Swap up to a certain amount of coins

    swap_all_balance    = False # True / False. If True, then swap the entire balance
    min_amount_swap     = 0 # If the balance is less than this amount, no swap will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)

    slippage = 1 # Slippage, default is from 1 to 3

class Value_Zerius_Refuel:

    '''
    Gas refuel via https://zerius.io

    from_chains : optimism | bsc | polygon | arbitrum | avalanche | fantom | linea | celo | zksync (temp disabled) | polygon_zkevm | nova | canto | zora | scroll | harmony | gnosis | core | base | mantle
    to_chains   : avalanche | bsc | arbitrum | optimism | fantom | harmony | celo | moonbeam | gnosis | metis | core | polygon_zkevm | canto | zksync | nova | zora | base | scroll
    '''

    from_chain = ['bsc'] # Networks from which you want to perform refuel (>= 1 network)
    to_chain   = ['core', 'metis', 'nova', 'gnosis', 'celo', 'moonbeam'] # Networks to which you want to perform refuel (>= 1 network)

    amount_from         = 0.000001 # Obtain from a certain amount of native token of the to_chain network
    amount_to           = 0.00002 # Obtain up to a certain amount of native token of the to_chain network

    swap_all_balance    = False # True / False. If True, then refuel the entire balance
    min_amount_swap     = 0 # If the balance is less than this amount, no refuel will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)

    get_layerzero_fee   = False # True if you want to check the gas. False if you want to perform refuel

class Value_NFT_Checker:
    
    '''
    NFT checker
    Chains: ethereum | optimism | bsc | polygon | arbitrum | avalanche | fantom | nova | zksync | polygon_zkevm | celo | gnosis | core | harmony | linea | base
    '''

    chain       = 'bsc' # Network to check NFTs
    contract    = '0x6848dbcb498b32675a83e88841facfcd43ef8e32' # NFT contract address
    min_balance = 1 # If the NFT balance is less than this amount, the wallet is flagged

class Value_Zerius_ONFT:

    '''
    https://zerius.io : Mint and bridge nft via layerzero; ideal for warming up networks.
    Chains : arbitrum | optimism | bsc | polygon | base | avalanche | ethereum | scroll | zksync | linea | nova | zora | polygon_zkevm | fantom | core | celo | harmony | canto
    '''

    class ValueMintBridge:
        '''Combination of minting and bridging operations'''

        from_chain  = ['polygon'] # Preferred source networks due to lower costs; selection is random if list is empty.
        to_chain    = ['scroll'] # Preferred destination networks due to lower costs; selection is random if list is empty.
        max_price   = 3 # Maximum acceptable cost for the process in dollars ($).
        amount      = [1, 2] # Range defining the minimum and maximum number of NFTs to be minted and bridged.

    class ValueMint:
        '''Minting operation'''

        chain = ['nova'] # The network where NFTs will be minted.
        amount_mint = [1, 1] # The exact number of NFTs to mint.

    class ValueBridge:
        '''
        Bridging operation
        This function locates NFTs in the source chain and bridges them to a randomly selected destination chain.
        '''

        from_chain  = ['bsc'] # The source network where NFTs will be searched; the final choice is random.
        to_chain    = ['celo', 'nova'] # Potential destination networks; the final choice is random.

        amount = 1 # The number of NFTs to bridge.
        bridge_all = True # If True, all available NFTs will be bridged if they exceed the specified 'amount'.

    class ValueUltra:
        '''
        Advanced strategy for cost-effective minting and bridging:
        1. Identifies all eligible networks with a native token valued at least $1.
        2. Determines the three most cost-effective bridging options for each network listed in 'included_chains'.
        3. Assesses the cost of minting across all networks.
        4. Strategically selects from the top three most affordable networks for combined minting and bridging operations. It starts with a random choice or based on 'from_chain' if specified.
        5. Skips minting if NFTs already exist in the initial network, otherwise initiates minting.
        6. Limits minting to the first network, while subsequent operations focus solely on bridging.
        7. Continuously selects from the three most affordable networks for bridging, based on random choice.
        '''

        max_bridge_price = 2.5 # The maximum price (in $) for bridging; any network exceeding this cost is ignored.
        bridges_count = [2, 4] # The range indicating the minimum and maximum number of bridges to execute.
        from_chain = [] # Can remain unspecified; the script autonomously selects the most cost-effective network from 'included_chains'.
        included_chains = ['optimism', 'scroll', 'arbitrum', 'bsc', 'avalanche', 'base', 'zksync'] # A list of potential networks, must specify at least two.

    max_waiting_nft = 120 # Maximum duration (in seconds) to await the arrival of the NFT in the destination network before timing out.

class Value_Starkgate:

    '''
    Bridge from Ethereum to Starknet via Starkgate (https://starkgate.starknet.io/)
    Warning! Add starknet addresses to data/starknet_address.txt
    '''

    amount_from         = 0.005 # Bridge from a certain amount of coins
    amount_to           = 0.005 # Bridge up to a certain amount of coins

    bridge_all_balance  = True # True / False. If True, then bridge the entire balance
    min_amount_bridge   = 0 # If the balance is less than this amount, no bridge will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)

class Value_BaseBridge:

    '''
    Bridge from Ethereum to Base via Bridge Base (https://bridge.base.org/deposit)
    '''

    amount_from         = 0.002 # Bridge from a certain amount of coins
    amount_to           = 0.002 # Bridge up to a certain amount of coins

    bridge_all_balance  = False # True / False. If True, then bridge the entire balance
    min_amount_bridge   = 0 # If the balance is less than this amount, no bridge will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)

class Value_ArbitrumBridge:

    '''
    Bridge from Ethereum to Arbitrum One / Arbitrum Nova via Arbitrum Bridge (https://bridge.arbitrum.io/?l2ChainId=42161)
    '''

    to_chain            = "nova" # To which network : arbitrum | nova

    amount_from         = 0.001 # Bridge from a certain amount of coins
    amount_to           = 0.002 # Bridge up to a certain amount of coins

    bridge_all_balance  = False # True / False. If True, then bridge the entire balance
    min_amount_bridge   = 0 # If the balance is less than this amount, no bridge will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)

class Value_ZoraBridge:

    '''
    Bridge from Ethereum to Zora via Bridge Zora (https://bridge.zora.energy/)
    '''

    amount_from         = 0.002 # Bridge from a certain amount of coins
    amount_to           = 0.002 # Bridge up to a certain amount of coins

    bridge_all_balance  = False # True / False. If True, then bridge the entire balance
    min_amount_bridge   = 0 # If the balance is less than this amount, no bridge will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)

class Value_ZkSyncBridge:

    '''
    Bridge from Ethereum to ZkSync via txSync Bridge (https://portal.txsync.io/bridge/)
    '''

    amount_from         = 0.002 # Bridge from a certain amount of coins
    amount_to           = 0.002 # Bridge up to a certain amount of coins

    bridge_all_balance  = True # True / False. If True, then bridge the entire balance
    min_amount_bridge   = 0 # If the balance is less than this amount, no bridge will be made
    keep_value_from     = 0 # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
    keep_value_to       = 0 # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)