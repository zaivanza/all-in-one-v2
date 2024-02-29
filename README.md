[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=All-in-one+V2)](https://git.io/typing-svg)

The README in English can be found here: [README_eng.md](https://github.com/zaivanza/all-in-one-v2/blob/main/README_eng.md).

Идеальный софт для ведения фермы.

## Основные модули

1. **evm_balance_checker**: Асинхронная проверка баланса любых токенов в любой EVM сети.
2. **starknet_balance_checker**: Асинхронная проверка баланса токенов в Starknet.
3. **debank_checker**: Асинхронная проверка всех токенов, NFT и протоколов в EVM сетях, доступных на [DeBank](https://debank.com/).
4. **exchange_withdraw**: Вывод монет с таких бирж, как Binance, MEXC, KuCoin, Bybit, Huobi, Bitget, CoinEx.
5. **[okx_withdraw](https://www.okx.com/)**: Вывод с биржи OKX, включая вывод с суб-аккаунтов, представлен как отдельный модуль.
6. **transfer**: Трансфер (перевод) монет с кошельков в EVM сетях.
7. **0x_swap**: Агрегатор, альтернатива 1inch для обмена токенов.
8. **[orbiter](https://www.orbiter.finance/)**: Бридж ETH во всех сетях. Для бриджа на StarkNet необходимо добавить адреса в `starknet_address.txt`.
9. **[woofi_bridge](https://fi.woo.org/)**: Бридж через WooFi (LayerZero), поддерживает все доступные монеты и сети.
10. **[woofi_swap](https://fi.woo.org/)**: Обмен токенов через WooFi, доступны все монеты и сети.
11. **[sushiswap](https://www.sushi.com/swap)**: Обмен токенов, поддерживает все основные сети, кроме Optimism.
12. **[bungee_refuel](https://www.bungee.exchange/refuel)**: Бридж для нативных токенов между сетями.
13. **tx_checker**: Проверка nonce во всех EVM сетях.
14. **[1inch_swap](https://app.1inch.io/)**: Агрегатор для обмена токенов.
15. **[zerkly_refuel](https://zerius.io/)**: Рефуел газа между сетями через LayerZero.
16. **nft_checker**: Асинхронная проверка баланса NFT.
17. **[zerius_onft](https://zerius.io/)**: Минт и бридж NFT через LayerZero.
18. **[starkgate_bridge](https://starkgate.starknet.io/)**: Бридж с Ethereum на StarkNet.
19. **[base_bridge](https://bridge.base.org/deposit)**: Бридж с Ethereum на Base.
20. **[arbitrum_bridge](https://bridge.arbitrum.io/?l2ChainId=42161)**: Бридж с Ethereum на Arbitrum One / Arbitrum Nova.
21. **[zora_bridge](https://bridge.zora.energy/)**: Бридж с Ethereum на Zora.
22. **[zksync_bridge](https://portal.txsync.io/bridge/)**: Бридж с Ethereum на zkSync.

## Дополнительная Информация

- Все результаты дублируются в терминал и телеграм-бота.
- **evm_balance_checker** и **nft_checker** используют multicall для ускорения трекинга.
- Возможность включить прокси в web3. Работает это так : берет все твои кошельки и поочередно берет прокси из файла `proxies.txt`. То есть распределение на прокси будет равным. Кол-во кошельков и прокси может отличаться. Например, если будет 10 кошельков и 3 прокси, то распределение будет такое : прокси_1 = 4 кошелька, прокси_2 = 3 кошелька, прокси_3 = 3 кошелька.
- Для каждой сети установлена максимальная плата за газ. Если стоимость газа превышает установленный лимит, скрипт ожидает снижения цены (`setting.py => MAX_GAS_CHARGE`).
- Транзакции, висящие в статусе pending более установленного времени (`config.py => max_time_check_tx_status`), автоматически считаются выполненными чтобы избежать задержек, особенно в сети BSC.
- Модули могут запускаться как поодиночке, так и группами через `tracks.py`.
- Асинхронность: поддержка одновременного запуска нескольких кошельков.

# Настройка

1. Вся настройка делается в файле `setting.py`, описание там же. Нужно переименовать `setting_EXAMPLE.py` на `setting.py`
2. Если хочешь запускать несколько модулей в одной цепочке, их нужно настраивать в `tracks.py`.
3. Переименуй папку `datas_EXAMPLE` на `datas`.
4. В папке `datas` есть 5 файлов :
- `wallets.txt` - сюда записываем кошельки (приватники / адреса).
- `recipients.txt` - сюда записываем адреса для трансфера, используется только в модуле transfer когда выводим с кошелька на адрес. 1 кошелек = 1 адрес.
- `proxies.txt` - сюда записываем прокси, они используются в debank чекере, без них он работать не будет, и в web3, если `USE_PROXY = True` (в конфиге). Формат : http://login:password@ip:port
- `starknet_address.txt` - сюда записываем адреса кошельков старкнета. если не будете бриджить с орбитера на старкнет, можно не вставлять.
- `data.py` - здесь вся приватная информация : rpc, tg_token, tg_id, апи ключи от бирж.
5. Настраивать модули нужно в классах value в файле `setting.py`.
6. Запускать нужно файл `main.py`, если `USE_TRACKS = False`, тогда в терминале будет список с модулями, нужно будет выбрать один.

# Информация по tracks (несколько модулей)

1. Чтобы режим работал, нужно в `setting.py` сделать `USE_TRACKS = True`.
2. В `tracks.py` настраиваются треки с модулями, можешь сделать несколько треков и выбирать их в `setting.py` в переменной `TRACK`.
3. Функция `wait_balance` работает только в режиме треков : выбираешь сеть, в которой будешь ждать монету, и минимальный баланс. Когда баланс монеты станет больше `min_balance`, скрипт перейдет к следующему модулю. Проверка баланса каждые 10 секунд. 

Устанавливаем библиотеки : `pip install -r requirements.txt`

> Внимание! Код может быть с ошибками, и за потерянные деньги мы отвественность не несем. Советую сначала все тестировать на маленькие суммы. Огромная просьба сначала все прочитать на 10 раз, все протестировать, погуглить и только потом задавать вопросы в наш код чат. В личку админам с вопросами по коду просьба не писать, они не ответят.

## Донаты (EVM): 
- `0xb7415DB78c886c67DBfB25D3Eb7fcd496dAf9021`
- `donates-for-hodlmod.eth`

## Links:
- https://t.me/links_hodlmodeth
- Code chat: [[ code ]](https://t.me/code_hodlmodeth)
- Ультимативный гайд по запуску скриптов на python : https://teletype.in/@hodlmod.eth/how-to-run-scripts