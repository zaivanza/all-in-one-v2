[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=All-in-one+V2)](https://git.io/typing-svg)

Perfect Script for Farming Management.

## Modules:

1. **evm_balance_checker**: Quickly (asynchronously) checks the balance of any token on any EVM network.
2. **starknet_balance_checker**: Quickly (asynchronously) checks the balance of tokens on Starknet network.
3. **debank_checker**: Swiftly (asynchronously) inspects tokens, NFTs, and protocols across multiple EVM networks (available on [DeBank](https://debank.com/)).
4. **exchange_withdraw**: Withdraws assets from exchanges like Binance, MEXC, KuCoin, Bybit, Huobi, and Bitget.
5. **[okx_withdraw](https://www.okx.com/)**: Withdraws assets from the OKX exchange, including sub-account withdrawals (handled as a separate module due to sub-account functionality).
6. **transfer**: Transfers assets from wallets to EVM networks.
7. **0x_swap**: Utilizes an aggregator as an alternative to 1inch for token swaps.
8. **[orbiter](https://www.orbiter.finance/)**: Bridges Ethereum assets to various networks, including ZKSync Era and StarkNet. To bridge to StarkNet, add StarkNet wallet addresses to the `starknet_address.txt` file.
9. **[woofi_bridge](https://fi.woo.org/)**: Bridges assets using the WooFi bridge via Stargate (LayerZero), supporting a wide range of tokens and networks.
10. **[woofi_swap](https://fi.woo.org/)**: Swaps tokens using the WooFi swap feature, which is versatile and supports numerous tokens and networks.
11. **[sushiswap](https://www.sushi.com/swap)**: Executes swaps on SushiSwap, accessible on major networks except for Optimism (currently).
12. **[bungee_refuel](https://www.bungee.exchange/refuel)**: Cost-effective bridge for transferring native tokens between networks.
13. **tx_checker**: Monitors nonces across nearly all EVM networks.
14. **[1inch_swap](https://app.1inch.io/)**: Leverages the 1inch aggregator for token swaps.
15. **[zerius_refuel](https://zerius.io/)**: Transfers gas from one network to another via LayerZero.
16. **nft_checker**: Swiftly (asynchronously) checks the balance of specific NFTs.
17. **[zerius_onft](https://zerius.io/)**: Mint and bridge nft via layerzero; ideal for warming up networks.
18. **[starkgate_bridge](https://starkgate.starknet.io/)**: Bridge from Ethereum to Starknet. 
19. **[base_bridge](https://bridge.base.org/deposit)**: Bridge from Ethereum to Base.
20. **[arbitrum_bridge](https://bridge.arbitrum.io/?l2ChainId=42161)**: Bridge from Ethereum to Arbitrum One / Arbitrum Nova.
21. **[zora_bridge](https://bridge.zora.energy/)**: Bridge from Ethereum to Zora.
22. **[zksync_bridge](https://portal.txsync.io/bridge/)**: Bridge from Ethereum to ZkSync.

## Additional Information:

- All results are duplicated to the terminal and a Telegram bot.
- **evm_balance_checker** and **nft_checker** use multicall to speed up tracking.
- The ability to enable proxies in web3. It works as follows: it takes all your wallets and sequentially uses proxies from the `proxies.txt` file. Thus, the distribution of proxies will be even. The number of wallets and proxies may differ. For example, if there are 10 wallets and 3 proxies, the distribution will be: proxy_1 = 4 wallets, proxy_2 = 3 wallets, proxy_3 = 3 wallets.
- A maximum gas fee is set for each network. If the gas cost exceeds the set limit, the script will wait for the price to decrease (`setting.py => MAX_GAS_CHARGE`).
- Transactions that remain in pending status for more than the set time (`config.py => max_time_check_tx_status`) are automatically considered completed to avoid delays, especially in the BSC network.
- Modules can be run individually or in groups through `tracks.py`.
- Asynchrony: support for simultaneous running of multiple wallets.

# Configuration

To configure the script:

1. Adjust settings in the `setting.py` file, following the descriptions within.
2. If you plan to run multiple modules sequentially, configure them in the `tracks.py` file.
3. In the `data` folder, rename files as follows: `wallets_EXAMPLE.txt` to `wallets.txt`, `proxies_EXAMPLE.txt` to `proxies.txt`, `data_EXAMPLE.py` to `data.py`.
4. Within the `data` folder, you'll find five files:
   - `wallets.txt`: Add wallets (private keys/addresses) here.
   - `recipients.txt`: Add recipient addresses for transfers, used in the transfer module when transferring from a wallet to an address. One wallet corresponds to one address.
   - `proxies.txt`: Add proxies for use in the debank checker. They are also used in web3 if `USE_PROXY = True` (in the config). The format is: `http://login:password@ip:port`.
   - `starknet_address.txt`: Add StarkNet wallet addresses here. Skip this step if you're not bridging from Orbiter to StarkNet.
   - `data.py`: Contains all the private information, such as RPC, tg_token, tg_id, API keys for exchanges.
5. Configure the modules in the `value` classes in the `setting.py` file.
6. Execute the `main.py` file. If `USE_TRACKS = False`, a list of modules will appear in the terminal, and you can select one.

# Using Tracks (Running Multiple Modules)

To enable track mode:

1. Set `USE_TRACKS = True` in `setting.py`.
2. In `tracks.py`, configure tracks with modules. You can create multiple tracks and select them in `setting.py` using the `TRACK` variable.
3. The `wait_balance` function works only in track mode: Select a network where you want to wait for a coin and set the minimum balance. When the coin's balance exceeds `min_balance`, the script advances to the next module, with balance checks every 10 seconds.

# Installation

Install the required libraries by running: `pip install -r requirements.txt`

> Please exercise caution when using the code, as it may contain errors. We are not responsible for any losses. It is advisable to conduct thorough testing with small amounts before proceeding. We kindly request that you read the instructions carefully, perform testing, and conduct online research before reaching out with questions in the code chat. Please refrain from sending code-related queries to admins privately, as they will not respond.

## Donations (EVM): 
- `0xb7415DB78c886c67DBfB25D3Eb7fcd496dAf9021`
- `donates-for-hodlmod.eth`

## Links:
- https://t.me/links_hodlmodeth
- Code chat: [[ code ]](https://t.me/code_hodlmodeth)