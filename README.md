[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=All-in-one+V2)](https://git.io/typing-svg)

Perfect Script-V2 for Farming Management.

## Modules:

1. **web3_checker**: Quickly (asynchronously) checks the balance of any token on any EVM network.
2. **debank_checker**: Swiftly (asynchronously) inspects tokens, NFTs, and protocols across multiple EVM networks (available on [DeBank](https://debank.com/)).
3. **exchange_withdraw**: Withdraws assets from exchanges like Binance, MEXC, KuCoin, Bybit, Huobi, and Bitget.
4. **okx_withdraw**: Withdraws assets from the OKX exchange, including sub-account withdrawals (handled as a separate module due to sub-account functionality).
5. **transfer**: Transfers assets from wallets to EVM networks.
6. **0x_swap**: Utilizes an aggregator as an alternative to 1inch for token swaps.
7. **[orbiter](https://www.orbiter.finance/)**: Bridges Ethereum assets to various networks, including ZKSync Era and StarkNet. To bridge to StarkNet, add StarkNet wallet addresses to the `starknet_address.txt` file.
8. **[woofi](https://fi.woo.org/)**: Bridges assets using the WooFi bridge via Stargate (LayerZero), supporting a wide range of tokens and networks.
9. **[woofi](https://fi.woo.org/)**: Swaps tokens using the WooFi swap feature, which is versatile and supports numerous tokens and networks.
10. **sushiswap**: Executes swaps on SushiSwap, accessible on major networks except for Optimism (currently).
11. **bungee_refuel**: Cost-effective bridge for transferring native tokens between networks.
12. **tx_checker**: Monitors nonces across nearly all EVM networks.
13. **1inch_swap**: Leverages the 1inch aggregator for token swaps.
14. **zerius_refuel**: Transfers gas from one network to another via LayerZero.
15. **nft_checker**: Swiftly (asynchronously) checks the balance of specific NFTs.
16. **[zerius_onft](https://zerius.io/)**: Mint and bridge nft via layerzero; ideal for warming up networks.
17. **starkgate_bridge**: Official bridge from Ethereum to Starknet. 
18. **base_bridge**: Official bridge from Ethereum to Base.

## Additional Information:

1. All results are logged not only in the terminal but also sent to a Telegram bot.
2. **web3_checker** and **nft_checker** use multicall for fast tracking.
3. You can enable proxies in **web3_checker**: It balances the distribution of wallets among specified proxies. For example, if you have 10 wallets and 3 proxies, it distributes as Proxy 1 = 4 wallets, Proxy 2 = 3 wallets, Proxy 3 = 3 wallets.
4. There's a maximum gas fee setting in $ for each network, and the script will sleep if gas prices exceed this threshold (`setting.py => MAX_GAS_CHARGE`).
5. Transactions pending for longer than the specified time (`config.py => max_time_check_tx_status`) are considered executed.
6. For **0x_swap**, an API key is required, which can be obtained [here](https://dashboard.0x.org/apps). Detailed instructions are available [here](https://t.me/never_broke_again_v1/315).
7. You can run one or multiple modules simultaneously. Configuration for running multiple modules is found in `tracks.py`.
8. For **1inch_swap**, an API key is required, which can be obtained [here](https://portal.1inch.dev/dashboard).
9. Asynchronous execution allows you to run multiple wallets concurrently.

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

Please exercise caution when using the code, as it may contain errors. We are not responsible for any losses. It is advisable to conduct thorough testing with small amounts before proceeding.

We kindly request that you read the instructions carefully, perform testing, and conduct online research before reaching out with questions in the code chat. Please refrain from sending code-related queries to admins privately, as they will not respond.

# Donations

Donations (EVM): `0xb7415DB78c886c67DBfB25D3Eb7fcd496dAf9021` or `donates-for-hodlmod.eth`

For updates and entertaining content, join our public chat: [hodlmodeth](https://t.me/hodlmodeth) and our [[ code ]](https://t.me/code_hodlmodeth) chat. You can also follow our channel for updates and fun content: [never_broke_again_v1](https://t.me/never_broke_again_v1).


# Reamde на русском.

Идеальный скрипт-V2 для ведения фермы. Освоив его, ты сможешь (идет перечисление модулей) :

1. web3_checker : очень быстро (асинка) смотрит баланс монеты в любой evm сети.
2. debank_checker : около быстро (асинка) смотрит все токены, нфт и протоколы во всех evm сетях (которые доступны на самом [debank](https://debank.com/)). 
3. exchange_withdraw : вывод монет с бирж : binance, mexc, kucoin, bybit, huobi, bitget.
4. okx_withdraw : вывод с биржи okx + в подарок вывод с субов. отдельным модулем из-за функции вывода с суб-аккаунтов.
5. transfer : вывод монет с кошельков в evm сетях.
6. 0x_swap : аграгатор, хорошая замена 1inch.
7. [orbiter](https://www.orbiter.finance/) : бридж eth во всех сетях, включая zksync era и starknet. чтобы бриджит на starknet, нужно добавить адреса кошельков старкнета в файл `starknet_address.txt`.
8. [woofi](https://fi.woo.org/) : bridge. бридж проходит через stargate (layerzero). универсален, доступны все монеты и сети, которые там есть. 
9. [woofi](https://fi.woo.org/) : swap. универсален, доступны все монеты и сети, которые там есть. 
10. sushiswap : универсальный, доступны все основные сети, кроме optimism (пока что).
11. bungee_refuel : дешевый бридж нативки между сетями.
12. tx_checker : смотрит nonce во всех (почти) evm сетях.
13. 1inch_swap : агрегатор. 
14. merkly_refuel : отправка газа с одной сети в другую через layerzero.
15. nft_checker : очень быстро (асинка) смотрит баланс конкретной nft.
16. [zerius](https://zerius.io/) : минт и бридж нфт через layerzero. более подробно здесь : https://t.me/hodlmodeth/339
17. starkgate_bridge : официальный бридж с ethereum на starknet. 
18. base_bridge : официальный бридж с ethereum на base.

Дополнительная информация :
1. Все результаты прописываются не только в терминал, но и в тг-бота.
2. web3_checker и nft_checker используют multicall => трекинг происходит очень быстро.
3. Возможность включить прокси в web3. Работает это так : берет все твои кошельки и поочередно берет прокси из файла `proxies.txt`. То есть распределение на прокси будет равным. Кол-во кошельков и прокси может отличаться. Например, если будет 10 кошельков и 3 прокси, то распределение будет такое : прокси_1 = 4 кошелька, прокси_2 = 3 кошелька, прокси_3 = 3 кошелька.
4. Добавил максимальную плату за газ в $ для каждой сети. если газ в транзе будет выше заданного числа, скрипт будет спать, пока газ не снизится (`setting.py => MAX_GAS_CHARGE`)
5. Если транзакция висит в пендинге > заданного времени (`config.py => max_time_check_tx_status`), она считается исполненной. это я сделал из-за bsc, тк с 1 гвеем некоторые транзы висят в пендинге часами, и скрипт соответственно тоже.
6. Для 0x_swap требуется api key, который можно получить здесь : https://dashboard.0x.org/apps. Более подробно описал здесь : https://t.me/never_broke_again_v1/315
7. Можно запускать 1 или несколько модулей. Запуск нескольких модулей настраивается в `tracks.py`.
8. Для 1inch_swap требуется api key, который можно получить здесь : https://portal.1inch.dev/dashboard.
9. Асихронность : можно запускать одновременно несколько кошельков. 

# Настройка.

1. Вся настройка делается в файле `setting.py`, описание там же. 
2. Если хочешь запускать несколько модулей в одной цепочке, их нужно настраивать в `tracks.py`.
3. В папке `data` переименуй файлы `wallets_EXAMPLE.txt` => `wallets.txt`, `proxies_EXAMPLE.txt` => `proxies.txt`,  `data_EXAMPLE.py` => `data.py`
4. В папке `data` есть 5 файлов :
- `wallets.txt` - сюда записываем кошельки (приватники / адреса).
- `recipients.txt` - сюда записываем адреса для трансфера, используется только в модуле transfer когда выводим с кошелька на адрес. 1 кошелек = 1 адрес.
- `proxies.txt` - сюда записываем прокси, они используются в debank чекере, без них он работать не будет, и в web3, если `USE_PROXY = True` (в конфиге). Формат : http://login:password@ip:port
- `starknet_address.txt` - сюда записываем адреса кошельков старкнета. если не будете бриджить с орбитера на старкнет, можно не вставлять.
- `data.py` - здесь вся приватная информация : rpc, tg_token, tg_id, апи ключи от бирж.
5. Настраивать модули нужно в классах value в файле `setting.py`.
6. Запускать нужно файл `main.py`, если `USE_TRACKS = False`, тогда в терминале будет список с модулями, нужно будет выбрать один.

# Информация по tracks (несколько модулей).

1. Чтобы режим работал, нужно в `setting.py` сделать `USE_TRACKS = True`.
2. В `tracks.py` настраиваются треки с модулями, можешь сделать несколько треков и выбирать их в `setting.py` в переменной `TRACK`.
3. Функция `wait_balance` работает только в режиме треков : выбираешь сеть, в которой будешь ждать монету, и минимальный баланс. Когда баланс монеты станет больше `min_balance`, скрипт перейдет к следующему модулю. Проверка баланса каждые 10 секунд. 

Устанавливаем библиотеки : `pip install -r requirements.txt`

Внимание! Код может быть с ошибками, и за потерянные деньги мы отвественность не несем. Советую сначала все тестировать на маленькие суммы.

Огромная просьба сначала все прочитать на 10 раз, все протестировать, погуглить и только потом задавать вопросы в наш код чат. В личку админам с вопросами по коду просьба не писать, они не ответят.

Donate (evm) : `0xb7415DB78c886c67DBfB25D3Eb7fcd496dAf9021` or `donates-for-hodlmod.eth`

Паблик : https://t.me/hodlmodeth. [[ code ]](https://t.me/code_hodlmodeth) чат. Канал с обновлениями и лайф-рофл-контентом : https://t.me/never_broke_again_v1