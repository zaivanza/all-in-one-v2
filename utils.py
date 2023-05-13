import base64
import decimal
import hmac
import math
import random
import time

import ccxt
import requests
import telebot
from loguru import logger
from web3 import Web3

from config import DATA, ERC20_ABI, decimalToInt, sleeping, RECIPIENTS_WALLETS, intToDecimal, \
    PROXIES, ORBITER_AMOUNT, ORBITER_AMOUNT_STR, WOOFI_SWAP_CONTRACTS, WOOFI_PATH, LAYERZERO_CHAINS_ID, \
    WOOFI_BRIDGE_CONTRACTS, settings, ORBITER_MAKER, STARKNET_WALLETS, CONTRACTS_ORBITER_TO_STARKNET, STR_CANCEL, \
    STR_DONE
from data.abi.abi import ABI_WOOFI_SWAP, ABI_WOOFI_BRIDGE, ABI_ORBITER_TO_STARKNET

list_send = []


def send_msg():
    try:

        str_send = '\n'.join(list_send)
        bot = telebot.TeleBot(settings['TELEGRAM']['tg_token'])
        bot.send_message(settings['TELEGRAM']['tg_id'], str_send, parse_mode='html')

    except Exception as error:
        logger.error(error)


# ============ web3_helpers ============

def evm_wallet(key):
    try:
        web3 = Web3(Web3.HTTPProvider(DATA['ethereum']['rpc']))
        wallet = web3.eth.account.from_key(key).address
        return wallet
    except:
        return key


def sign_tx(web3, contract_txn, privatekey):
    signed_tx = web3.eth.account.sign_transaction(contract_txn, privatekey)
    raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash = web3.to_hex(raw_tx_hash)

    return tx_hash


def check_data_token(web3, token_address):
    try:

        token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        symbol = token_contract.functions.symbol().call()

        return token_contract, decimals, symbol

    except Exception as error:
        logger.error(error)


def check_status_tx(chain, tx_hash):
    logger.info(f'{chain} : checking tx_status : {tx_hash}')

    while True:
        try:
            rpc_chain = DATA[chain]['rpc']
            web3 = Web3(Web3.HTTPProvider(rpc_chain))
            status_ = web3.eth.get_transaction_receipt(tx_hash)
            status = status_["status"]
            if status in [0, 1]:
                return status
            time.sleep(1)
        except Exception as error:
            # logger.info(f'error, try again : {error}')
            time.sleep(1)


def add_gas_limit(web3, contract_txn):
    try:
        value = contract_txn['value']
        contract_txn['value'] = 0
        pluser = [1.3, 1.7]
        gasLimit = web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
        # logger.info(f"gasLimit : {contract_txn['gas']}")
    except Exception as error:
        contract_txn['gas'] = random.randint(2000000, 3000000)
        logger.info(f"estimate_gas error : {error}. random gasLimit : {contract_txn['gas']}")

    contract_txn['value'] = value
    return contract_txn


def add_gas_limit_layerzero(web3, contract_txn):
    try:
        pluser = [1.3, 1.7]
        gasLimit = web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
        # logger.info(f"gasLimit : {contract_txn['gas']}")
    except Exception as error:
        contract_txn['gas'] = random.randint(2000000, 3000000)
        logger.info(f"estimate_gas error : {error}. random gasLimit : {contract_txn['gas']}")

    return contract_txn


def add_gas_price(web3, contract_txn):
    try:
        gas_price = web3.eth.gas_price
        contract_txn['gasPrice'] = int(gas_price * random.uniform(1.05, 1.08))
    except Exception as error:
        logger.error(error)

    return contract_txn


def round_to(num, digits=3):
    try:
        if num == 0:
            return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits:
            scale = digits
        return round(num, scale)
    except:
        return num


def check_balance(privatekey, chain, address_contract):
    try:

        rpc_chain = DATA[chain]['rpc']
        web3 = Web3(Web3.HTTPProvider(rpc_chain))

        try:
            wallet = web3.eth.account.from_key(privatekey).address
        except:
            wallet = privatekey

        if address_contract == '':  # eth
            balance = web3.eth.get_balance(web3.to_checksum_address(wallet))
            token_decimal = 18
        else:
            token_contract, token_decimal, symbol = check_data_token(web3, address_contract)
            balance = token_contract.functions.balanceOf(web3.to_checksum_address(wallet)).call()

        human_readable = decimalToInt(balance, token_decimal)

        # cprint(human_readable, 'blue')

        return human_readable

    except Exception as error:
        logger.error(error)
        time.sleep(1)
        check_balance(privatekey, chain, address_contract)


def check_allowance(chain, token_address, wallet, spender):
    try:
        web3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        amount_approved = contract.functions.allowance(wallet, spender).call()
        return amount_approved
    except Exception as error:
        logger.error(error)


# ============== modules ==============

def approve_(amount, private_key, chain, token_address, spender, retry=0):
    try:

        web3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        # web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        spender = Web3.to_checksum_address(spender)

        wallet = web3.eth.account.from_key(private_key).address
        contract, decimals, symbol = check_data_token(web3, token_address)

        module_str = f'approve : {symbol}'

        allowance_amount = check_allowance(chain, token_address, wallet, spender)

        if amount > allowance_amount:

            contract_txn = contract.functions.approve(
                spender,
                115792089237316195423570985008687907853269984665640564039457584007913129639935
            ).build_transaction(
                {
                    "chainId": web3.eth.chain_id,
                    "from": wallet,
                    "nonce": web3.eth.get_transaction_count(wallet),
                    'gasPrice': 0,
                    'gas': 0,
                    "value": 0
                }
            )

            if chain == 'bsc':
                contract_txn['gasPrice'] = random.randint(1000000000, 1050000000) # специально ставим 1 гвей, так транза будет дешевле
            else:
                contract_txn = add_gas_price(web3, contract_txn)
            contract_txn = add_gas_limit(web3, contract_txn)

            tx_hash = sign_tx(web3, contract_txn, private_key)
            tx_link = f'{DATA[chain]["scan"]}/{tx_hash}'

            status = check_status_tx(chain, tx_hash)

            if status == 1:
                logger.success(f"{module_str} | {tx_link}")
                sleeping(5, 5)
            else:
                logger.error(f"{module_str} | tx is failed | {tx_link}")
                if retry < settings['RETRY']:
                    logger.info(f"try again in 10 sec.")
                    sleeping(10, 10)
                    approve_(private_key, chain, token_address, spender, retry + 1)

    except Exception as error:
        logger.error(f'{error}')
        if retry < settings['RETRY']:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            approve_(private_key, chain, token_address, spender, retry + 1)


def transfer(private_key, retry=0):
    try:

        to_address = RECIPIENTS_WALLETS[private_key]
        chain = settings['value_transfer']['chain']
        amount_from = settings['value_transfer']['amount_from']
        amount_to = settings['value_transfer']['amount_to']
        transfer_all_balance = settings['value_transfer']['transfer_all_balance']
        min_amount_transfer = settings['value_transfer']['min_amount_transfer']
        keep_value_from = settings['value_transfer']['keep_value_from']
        keep_value_to = settings['value_transfer']['keep_value_to']
        token_address = settings['value_transfer']['token_address']

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)

        module_str = f'transfer => {to_address}'

        web3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))

        account = web3.eth.account.from_key(private_key)
        wallet = account.address
        nonce = web3.eth.get_transaction_count(wallet)

        if token_address == '':
            decimals = 18
            symbol = DATA[chain]['token']
        else:
            token_contract, decimals, symbol = check_data_token(web3, token_address)

        if transfer_all_balance:
            amount = check_balance(private_key, chain, token_address) - keep_value
        else:
            amount = round(random.uniform(amount_from, amount_to), 8)

        value = intToDecimal(amount, decimals)

        if amount >= min_amount_transfer:

            if token_address == '':

                contract_txn = {
                    'chainId': web3.eth.chain_id,
                    'gasPrice': 0,
                    'nonce': nonce,
                    'gas': 0,
                    'to': Web3.to_checksum_address(to_address),
                    'value': int(value)
                }

            else:

                tx = {
                    'chainId': web3.eth.chain_id,
                    'gasPrice': 0,
                    'gas': 0,
                    'nonce': nonce,
                }

                contract_txn = token_contract.functions.transfer(Web3.to_checksum_address(to_address),
                                                                 int(value)).build_transaction(tx)

            contract_txn = add_gas_price(web3, contract_txn)
            contract_txn = add_gas_limit(web3, contract_txn)

            if token_address == '':
                if transfer_all_balance:
                    gas_price = contract_txn['gasPrice']
                    gas_limit = contract_txn['gas']
                    gas_gas = gas_price * gas_limit
                    contract_txn['value'] = int(value) - int(gas_gas)

            tx_hash = sign_tx(web3, contract_txn, private_key)
            tx_link = f'{DATA[chain]["scan"]}/{tx_hash}'

            module_str = f'transfer {round_to(amount)} {symbol} => {to_address}'

            status = check_status_tx(chain, tx_hash)
            if status == 1:
                logger.success(f'{module_str} | {tx_link}')
                list_send.append(f'{module_str}')
            else:
                if retry < settings['RETRY']:
                    logger.info(f'{module_str} | tx is failed, try again in 10 sec | {tx_link}')
                    sleeping(10, 10)
                    orbiter_bridge(private_key, retry + 1)
                else:
                    logger.error(f'{module_str} | tx is failed | {tx_link}')

        else:
            logger.error(
                f"{module_str} : can't transfer : {amount} (amount) < {min_amount_transfer} (min_amount_transfer)")
            list_send.append(f'{module_str} : {amount} < {min_amount_transfer}')

    except Exception as error:

        logger.error(f'{module_str} | {error}')
        if retry < settings['RETRY']:
            logger.info(f'try again | {wallet}')
            sleeping(10, 10)
            transfer(private_key, retry + 1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')

def get_api_call_data(url):

    def try_get_with_proxy():
        try:
            proxy = random.choice(PROXIES)
            # cprint(proxy, 'yellow')
            proxies = {
                'http': proxy,
                'https': proxy,
            }
            call_data = requests.get(url, proxies=proxies)
            return call_data
        except Exception as error:
            logger.error(error)
            call_data = requests.get(url)

    call_data = requests.get(url)

    # cprint(f'call_data.status_code : {call_data.status_code}', 'blue')

    if call_data.status_code == 200:
        api_data = call_data.json()
        return api_data

    else:

        call_data = try_get_with_proxy()

        if call_data.status_code == 200:
            api_data = call_data.json()
            return api_data

        else:

            try:
                api_data = call_data.json()
                logger.error(api_data['description'])
                return False

            except ValueError as error:
                logger.error(error)
                time.sleep(1)
                return get_api_call_data(url)

            except Exception as error:
                logger.error(error)
                return get_api_call_data(url)


def inch_swap(private_key, retry=0):
    try:

        inch_version = 5
        chain = settings['value_1inch_swap']['chain']
        swap_all_balance = settings['value_1inch_swap']['swap_all_balance']
        min_amount_swap = settings['value_1inch_swap']['min_amount_swap']
        keep_value_from = settings['value_1inch_swap']['keep_value_from']
        keep_value_to = settings['value_1inch_swap']['keep_value_to']
        amount_from = settings['value_1inch_swap']['amount_from']
        amount_to = settings['value_1inch_swap']['amount_to']
        from_token_address = settings['value_1inch_swap']['from_token_address']
        to_token_address = settings['value_1inch_swap']['to_token_address']
        slippage = settings['value_1inch_swap']['slippage']
        divider = settings['value_1inch_swap']['divider']

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)

        if chain == 'zksync':
            divider = divider
        else:
            divider = 1

        web3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        chain_id = web3.eth.chain_id

        if from_token_address == '':
            from_token_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            from_decimals = 18
            from_symbol = DATA[chain]['token']
        else:
            from_token_contract, from_decimals, from_symbol = check_data_token(web3, from_token_address)

        if to_token_address == '':
            to_token_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            to_symbol = DATA[chain]['token']
        else:
            to_token_contract, to_decimals, to_symbol = check_data_token(web3, to_token_address)

        account = web3.eth.account.from_key(private_key)
        wallet = account.address

        if swap_all_balance:
            amount = check_balance(private_key, chain, from_token_address) - keep_value
        else:
            amount = round(random.uniform(amount_from, amount_to), 8)

        amount = amount * 0.999
        amount_to_swap = intToDecimal(amount, from_decimals)

        spender_json = get_api_call_data(f'https://api.1inch.io/v{inch_version}.0/{chain_id}/approve/spender')
        spender = Web3.to_checksum_address(spender_json['address'])

        # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апруваем
        if from_token_address != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            approve_(amount_to_swap, private_key, chain, from_token_address, spender)

        _1inchurl = f'https://api.1inch.io/v{inch_version}.0/{chain_id}/swap?fromTokenAddress={from_token_address}&toTokenAddress={to_token_address}&amount={amount_to_swap}&fromAddress={wallet}&slippage={slippage}'
        json_data = get_api_call_data(_1inchurl)

        if json_data == False:

            logger.info('failed to swap in 1inch')

        else:

            # cprint(json_data, 'yellow')

            tx  = json_data['tx']
            tx['chainId'] = chain_id
            tx['nonce'] = web3.eth.get_transaction_count(wallet)
            tx['to'] = Web3.to_checksum_address(tx['to'])
            tx['gasPrice'] = int(tx['gasPrice'])
            tx['gas'] = int(int(tx['gas']) / divider)
            tx['value'] = int(tx['value'])

            # cprint(tx, 'blue')

            if chain == 'bsc':
                tx['gasPrice'] = random.randint(1000000000, 1050000000) # специально ставим 1 гвей, так транза будет дешевле

            if amount >= min_amount_swap:

                tx_hash     = sign_tx(web3, tx, private_key)
                tx_link     = f'{DATA[chain]["scan"]}/{tx_hash}'

                module_str = f'1inch_swap : {round_to(amount)} {from_symbol} => {to_symbol}'

                status  = check_status_tx(chain, tx_hash)

                if status == 1:
                    logger.success(f'{module_str} | {tx_link}')
                    list_send.append(f'{STR_DONE}{module_str}')
                else:
                    logger.error(f'{module_str} | tx is failed | {tx_link}')
                    if retry < settings['RETRY']:
                        logger.info(f'try again in 10 sec.')
                        sleeping(10, 10)
                        inch_swap(private_key, retry+1)

            else:
                logger.error(f"{module_str} : can't swap : {amount} (amount) < {min_amount_swap} (min_amount_swap)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} < {min_amount_swap}')

    except KeyError:
        logger.error(json_data['description'])
        module_str = f'1inch_swap'
        list_send.append(f'{STR_CANCEL}{module_str}')

    except Exception as error:
        module_str = f'1inch_swap'
        logger.error(f'{module_str} | error : {error}')
        if retry < settings['RETRY']:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            inch_swap(private_key, retry + 1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')


def okx_data(api_key, secret_key, pass_phras, request_path="/api/v5/account/balance?ccy=USDT", body='', meth="GET"):
    try:
        import datetime

        def signature(
                timestamp: str, method: str, request_path: str, secret_key: str, body: str = ""
        ) -> str:
            if not body:
                body = ""

            message = timestamp + method.upper() + request_path + body
            mac = hmac.new(
                bytes(secret_key, encoding="utf-8"),
                bytes(message, encoding="utf-8"),
                digestmod="sha256",
            )
            d = mac.digest()
            return base64.b64encode(d).decode("utf-8")

        dt_now = datetime.datetime.utcnow()
        ms = str(dt_now.microsecond).zfill(6)[:3]
        timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

        base_url = "https://www.okex.com"
        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": api_key,
            "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, secret_key, body),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": pass_phras,
            'x-simulated-trading': '0'
        }
    except Exception as ex:
        logger.error(ex)
    return base_url, request_path, headers


def okx_withdraw(private_key, retry=0):
    chain = settings['value_okx']['chain']
    symbol = settings['value_okx']['symbol']
    amount_from = settings['value_okx']['amount_from']
    amount_to = settings['value_okx']['amount_to']
    api_key = settings['CEX_KEYS']['okx']['api_key']
    api_secret = settings['CEX_KEYS']['okx']['api_secret']
    passphras = settings['CEX_KEYS']['okx']['passphras']
    fee = settings['value_okx']['fee']
    SUB_ACC = settings['value_okx']['SUB_ACC']
    AMOUNT = round(random.uniform(amount_from, amount_to), 7)

    wallet = evm_wallet(private_key)

    try:

        if SUB_ACC:

            _, _, headers = okx_data(api_key, api_secret, passphras, request_path=f"/api/v5/users/subaccount/list",
                                     meth="GET")
            list_sub = requests.get("https://www.okx.cab/api/v5/users/subaccount/list", timeout=10, headers=headers)
            list_sub = list_sub.json()

            for sub_data in list_sub['data']:
                name_sub = sub_data['subAcct']

                _, _, headers = okx_data(api_key, api_secret, passphras,
                                         request_path=f"/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy={symbol}",
                                         meth="GET")
                sub_balance = requests.get(
                    f"https://www.okx.cab/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy={symbol}", timeout=10,
                    headers=headers)
                sub_balance = sub_balance.json()
                sub_balance = sub_balance['data'][0]['bal']

                logger.info(f'{name_sub} | sub_balance : {sub_balance}')

                body = {"ccy": f"{symbol}", "amt": str(sub_balance), "from": 6, "to": 6, "type": "2",
                        "subAcct": name_sub}
                _, _, headers = okx_data(api_key, api_secret, passphras, request_path=f"/api/v5/asset/transfer",
                                         body=str(body), meth="POST")
                a = requests.post("https://www.okx.cab/api/v5/asset/transfer", data=str(body), timeout=10,
                                  headers=headers)
                a = a.json()
                time.sleep(1)

        try:
            _, _, headers = okx_data(api_key, api_secret, passphras,
                                     request_path=f"/api/v5/account/balance?ccy={symbol}")
            balance = requests.get(f'https://www.okx.cab/api/v5/account/balance?ccy={symbol}', timeout=10,
                                   headers=headers)
            balance = balance.json()
            balance = balance["data"][0]["details"][0]["cashBal"]
            # print(balance)

            if balance != 0:
                body = {"ccy": f"{symbol}", "amt": float(balance), "from": 18, "to": 6, "type": "0", "subAcct": "",
                        "clientId": "", "loanTrans": "", "omitPosRisk": ""}
                _, _, headers = okx_data(api_key, api_secret, passphras, request_path=f"/api/v5/asset/transfer",
                                         body=str(body), meth="POST")
                a = requests.post("https://www.okx.cab/api/v5/asset/transfer", data=str(body), timeout=10,
                                  headers=headers)
        except Exception:
            pass

        body = {"ccy": symbol, "amt": AMOUNT, "fee": fee, "dest": "4", "chain": f"{symbol}-{chain}", "toAddr": wallet}
        _, _, headers = okx_data(api_key, api_secret, passphras, request_path=f"/api/v5/asset/withdrawal",
                                 body=str(body), meth="POST")
        a = requests.post("https://www.okx.cab/api/v5/asset/withdrawal", data=str(body), timeout=10, headers=headers)
        result = a.json()
        # cprint(result, 'blue')

        if result['code'] == '0':
            logger.success(f"withdraw success => {wallet} | {AMOUNT} {SYMBOL}")
            list_send.append(f'{STR_DONE}okx_withdraw')
        else:
            error = result['msg']
            logger.error(f"withdraw unsuccess => {wallet} | error : {error}")
            list_send.append(f"{STR_CANCEL}okx_withdraw :  {result['msg']}")

    except Exception as error:
        logger.error(f"withdraw unsuccess => {wallet} | error : {error}")
        if retry < settings['RETRY']:
            logger.info(f"try again in 10 sec. => {wallet}")
            sleeping(10, 10)
            okx_withdraw(private_key, retry + 1)
        else:
            list_send.append(f'{STR_CANCEL}okx_withdraw')

def check_orbiter_limits(from_chain, to_chain):
    orbiter_ids = {
        'ethereum': '1',
        'optimism': '7',
        'bsc': '15',
        'arbitrum': '2',
        'nova': '16',
        'polygon': '6',
        'polygon_zkevm': '17',
        'zksync': '14',
        'zksync_lite': '3',
        'starknet': '4',
    }

    from_maker = orbiter_ids[from_chain]
    to_maker = orbiter_ids[to_chain]

    maker_x_maker = f'{from_maker}-{to_maker}'

    for maker in ORBITER_MAKER:

        if maker_x_maker == maker:
            min_bridge = ORBITER_MAKER[maker]['ETH-ETH']['minPrice']
            max_bridge = ORBITER_MAKER[maker]['ETH-ETH']['maxPrice']
            fees = ORBITER_MAKER[maker]['ETH-ETH']['tradingFee']

            return min_bridge, max_bridge, fees


def get_orbiter_value(base_num, chain):
    base_num_dec = decimal.Decimal(str(base_num))
    orbiter_amount_dec = decimal.Decimal(str(ORBITER_AMOUNT[chain]))
    difference = base_num_dec - orbiter_amount_dec
    random_offset = decimal.Decimal(str(random.uniform(-0.000000000000001, 0.000000000000001)))
    result_dec = difference + random_offset
    orbiter_str = ORBITER_AMOUNT_STR[chain][-4:]
    result_str = '{:.18f}'.format(result_dec.quantize(decimal.Decimal('0.000000000000000001')))
    result_str = result_str[:-4] + orbiter_str
    return decimal.Decimal(result_str)


def orbiter_bridge(private_key, retry=0):
    try:

        orbiter_min_bridge = 0.005

        from_chain = settings['value_orbiter']['from_chain']
        to_chain = settings['value_orbiter']['to_chain']
        bridge_all_balance = settings['value_orbiter']['bridge_all_balance']
        amount_from = settings['value_orbiter']['amount_from']
        amount_to = settings['value_orbiter']['amount_to']
        min_amount_bridge = settings['value_orbiter']['min_amount_bridge']
        keep_value_from = settings['value_orbiter']['keep_value_from']
        keep_value_to = settings['value_orbiter']['keep_value_to']

        module_str = f'orbiter_bridge : {from_chain} => {to_chain}'

        min_bridge, max_bridge, fees = check_orbiter_limits(from_chain, to_chain)
        min_bridge = min_bridge + fees

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if bridge_all_balance:
            amount = check_balance(private_key, from_chain, '') - keep_value
        else:
            amount = round(random.uniform(amount_from, amount_to), 8)
        amount_to_bridge = amount

        amount = get_orbiter_value(amount_to_bridge, to_chain)  # получаем нужный amount

        if (amount > min_bridge and amount < max_bridge):

            # cprint(amount, 'yellow')
            value = intToDecimal(amount, 18)

            web3 = Web3(Web3.HTTPProvider(DATA[from_chain]['rpc']))
            account = web3.eth.account.from_key(private_key)
            wallet = account.address
            chain_id = web3.eth.chain_id
            nonce = web3.eth.get_transaction_count(wallet)

            if amount >= min_amount_bridge:

                if to_chain == 'starknet':

                    starknet_address = STARKNET_WALLETS[private_key]
                    if starknet_address[:3] == '0x0':
                        starknet_wallet = f'030{starknet_address[3:]}'
                    else:
                        starknet_wallet = f'030{starknet_address[2:]}'

                    starknet_wallet = bytes.fromhex(starknet_wallet)

                    contract = web3.eth.contract(
                        address=Web3.to_checksum_address(CONTRACTS_ORBITER_TO_STARKNET[from_chain]),
                        abi=ABI_ORBITER_TO_STARKNET
                    )

                    contract_txn = contract.functions.transfer(
                        '0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8',  # _to
                        starknet_wallet
                    ).build_transaction(
                        {
                            'chainId': chain_id,
                            "from": wallet,
                            "nonce": nonce,
                            "value": value,
                            'gas': 0,
                            'gasPrice': 0
                        }
                    )

                else:

                    contract_txn = {
                        'chainId': chain_id,
                        'nonce': nonce,
                        'from': wallet,
                        'to': '0x80C67432656d59144cEFf962E8fAF8926599bCF8',
                        'value': value,
                        'gas': 0,
                        'gasPrice': 0
                    }


                if from_chain == 'bsc':
                    contract_txn['gasPrice'] = random.randint(1000000000, 1050000000) # специально ставим 1 гвей, так транза будет дешевле
                else:
                    contract_txn = add_gas_price(web3, contract_txn)
                contract_txn = add_gas_limit(web3, contract_txn)

                # cprint(contract_txn['value'], 'green')

                tx_hash = sign_tx(web3, contract_txn, private_key)
                tx_link = f'{DATA[from_chain]["scan"]}/{tx_hash}'

                status = check_status_tx(from_chain, tx_hash)
                if status == 1:
                    logger.success(f'{module_str} | {tx_link}')
                    list_send.append(f'{module_str}')

                else:
                    if retry < settings['RETRY']:
                        logger.info(f'{module_str} | tx is failed, try again in 10 sec | {tx_link}')
                        sleeping(10, 10)
                        orbiter_bridge(private_key, retry + 1)
                    else:
                        logger.error(f'{module_str} | tx is failed | {tx_link}')
                        list_send.append(f'{module_str} | tx is failed | {tx_link}')

            else:
                logger.error(f"{module_str} : can't bridge : {amount} (amount) < {min_amount_bridge} (min_amount_bridge)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} < {min_amount_bridge}')

        else:

            if amount < min_bridge:

                logger.error(f"{module_str} : can't bridge : {amount} (amount) < {min_bridge} (min_bridge)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} < {min_bridge}')

            elif amount > max_bridge:

                logger.error(f"{module_str} : can't bridge : {amount} (amount) > {max_bridge} (max_bridge)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} > {max_bridge}')

    except Exception as error:

        logger.error(f'{module_str} | {error}')
        if retry < settings['RETRY']:
            logger.info(f'try again | {wallet}')
            sleeping(10, 10)
            transfer(private_key, retry + 1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')

def woofi_get_min_amount(chain, from_token, to_token, amount):
    try:

        if from_token.upper() != to_token.upper():

            # cprint(f'{chain} : {from_token} => {to_token} | {amount}', 'blue')

            slippage = 0.95

            web3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
            address_contract = web3.to_checksum_address(WOOFI_SWAP_CONTRACTS[chain])
            contract = web3.eth.contract(address=address_contract, abi=ABI_WOOFI_SWAP)

            from_token = Web3.to_checksum_address(from_token)
            to_token = Web3.to_checksum_address(to_token)

            minToAmount = contract.functions.tryQuerySwap(
                from_token,
                to_token,
                amount
            ).call()

            return int(minToAmount * slippage)

        else:

            return int(amount)

    except Exception as error:
        logger.error(f'error : {error}. return 0')
        return 0


def woofi_bridge(private_key, from_chain, to_chain, from_token, to_token, swap_all_balance, amount_from, amount_to,
                 min_amount_swap, keep_value_from, keep_value_to, retry=0):
    try:

        def get_srcInfos(amount_, from_chain, from_token):

            web3 = Web3(Web3.HTTPProvider(DATA[from_chain]['rpc']))

            from_token = Web3.to_checksum_address(from_token)

            if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                token_contract, decimals, symbol = check_data_token(web3, from_token)
            else:
                decimals = 18

            amount = intToDecimal(amount_, decimals)
            bridgeToken = WOOFI_PATH[from_chain]
            minBridgeAmount = woofi_get_min_amount(from_chain, from_token, WOOFI_PATH[from_chain], amount)

            from_token = Web3.to_checksum_address(from_token)
            bridgeToken = Web3.to_checksum_address(bridgeToken)

            srcInfos = [
                from_token,
                bridgeToken,
                amount,
                minBridgeAmount
            ]

            return srcInfos

        def get_dstInfos(amount, to_chain, to_token):

            chainId = LAYERZERO_CHAINS_ID[to_chain]

            minToAmount = int(woofi_get_min_amount(to_chain, WOOFI_PATH[to_chain], to_token, amount) * 0.99)
            bridgeToken = WOOFI_PATH[to_chain]

            bridgeToken = Web3.to_checksum_address(bridgeToken)
            to_token = Web3.to_checksum_address(to_token)

            dstInfos = [
                chainId,
                to_token,  # toToken
                bridgeToken,  # bridgeToken
                minToAmount,  # minToAmount
                0  # airdropNativeAmount
            ]

            return dstInfos

        module_str = f'woofi_bridge : {from_chain} => {to_chain}'
        logger.info(module_str)

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance:
            amount_ = check_balance(private_key, from_chain, from_token) - keep_value
        else:
            amount_ = round(random.uniform(amount_from, amount_to), 8)

        web3 = Web3(Web3.HTTPProvider(DATA[from_chain]['rpc']))
        address_contract = web3.to_checksum_address(
            WOOFI_BRIDGE_CONTRACTS[from_chain]
        )

        if from_token != '':
            token_contract, decimals, symbol = check_data_token(web3, from_token)
        else:
            decimals = 18

        contract = web3.eth.contract(address=address_contract, abi=ABI_WOOFI_BRIDGE)
        wallet = web3.eth.account.from_key(private_key).address

        if to_token == '': to_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        if from_token == '': from_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        amount = intToDecimal(amount_, decimals)
        srcInfos = get_srcInfos(amount_, from_chain, from_token)

        if from_chain == 'bsc':
            amount_src = decimalToInt(srcInfos[3], 18)
            amount_src = intToDecimal(amount_src, 6)
        else:
            amount_src = srcInfos[3]

        dstInfos = get_dstInfos(amount_src, to_chain, to_token)

        # cprint(f'\nsrcInfos : {srcInfos}\ndstInfos : {dstInfos}', 'blue')

        # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апруваем
        if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            approve_(amount, private_key, from_chain, from_token, WOOFI_BRIDGE_CONTRACTS[from_chain])
            sleeping(5, 10)

        while True:
            try:
                fees = contract.functions.quoteLayerZeroFee(
                    random.randint(112101680502565000, 712101680502565000),  # refId
                    wallet,  # to
                    srcInfos,
                    dstInfos
                ).call()
                break
            except Exception as error:
                logger.error(error)
                time.sleep(1)

        if from_token == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            value = int(amount + fees[0])
        else:
            value = int(fees[0])

        if amount_ >= min_amount_swap:
            contract_txn = contract.functions.crossSwap(
                random.randint(112101680502565000, 712101680502565000),  # refId
                wallet,  # to
                srcInfos,
                dstInfos
            ).build_transaction(
                {
                    'from': wallet,
                    'nonce': web3.eth.get_transaction_count(wallet),
                    'value': value,
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            if from_chain == 'bsc':
                contract_txn['gasPrice'] = random.randint(1000000000, 1050000000) # специально ставим 1 гвей, так транза будет дешевле
            else:
                contract_txn = add_gas_price(web3, contract_txn)
            contract_txn = add_gas_limit_layerzero(web3, contract_txn)

            if swap_all_balance:
                if from_token == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                    gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                    contract_txn['value'] = contract_txn['value'] - gas_gas

            tx_hash = sign_tx(web3, contract_txn, private_key)
            tx_link = f'{DATA[from_chain]["scan"]}/{tx_hash}'

            status = check_status_tx(from_chain, tx_hash)
            if status == 1:
                logger.success(f'{module_str} | {tx_link}')
                list_send.append(f'{STR_DONE}{module_str}')
                time.sleep(3)

            else:
                logger.error(f'{module_str} | tx is failed | {tx_link}')

                retry += 1
                if retry < settings['RETRY']:
                    logger.info(f'try again | {wallet}')
                    time.sleep(3)
                    woofi_bridge(private_key, from_chain, to_chain, from_token, to_token, swap_all_balance, amount_from,
                                 amount_to, min_amount_swap, keep_value_from, keep_value_to, retry + 1)
                else:
                    list_send.append(f'{STR_CANCEL}{module_str}')

        else:
            logger.error(f"{module_str} : can't bridge : {amount_} (amount) < {min_amount_swap} (min_amount_swap)")
            list_send.append(f'{STR_CANCEL}{module_str} : {amount_} < {min_amount_swap}')

    except Exception as error:
        logger.error(f'{module_str} | error : {error}')
        if retry < settings['RETRY']:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            woofi_bridge(private_key, from_chain, to_chain, from_token, to_token, swap_all_balance, amount_from,
                         amount_to, min_amount_swap, keep_value_from, keep_value_to, retry + 1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')


def woofi_swap(privatekey, from_chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap,
               keep_value_from, keep_value_to, retry=0):
    try:

        module_str = f'woofi_swap : {from_chain}'
        logger.info(module_str)

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance:
            amount_ = check_balance(privatekey, from_chain, from_token) - keep_value
        else:
            amount_ = round(random.uniform(amount_from, amount_to), 8)

        web3 = Web3(Web3.HTTPProvider(DATA[from_chain]['rpc']))
        address_contract = web3.to_checksum_address(
            WOOFI_SWAP_CONTRACTS[from_chain]
        )

        if to_token == '':
            to_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        if from_token == '':
            from_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        from_token = Web3.to_checksum_address(from_token)
        to_token = Web3.to_checksum_address(to_token)

        if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            token_contract, decimals, symbol = check_data_token(web3, from_token)
        else:
            decimals = 18

        contract = web3.eth.contract(address=address_contract, abi=ABI_WOOFI_SWAP)
        wallet = web3.eth.account.from_key(privatekey).address

        amount = intToDecimal(amount_, decimals)

        # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апруваем
        if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            approve_(amount, privatekey, from_chain, from_token, WOOFI_SWAP_CONTRACTS[from_chain])
            sleeping(5, 10)

        if from_token == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            value = amount
        else:
            value = 0

        minToAmount = woofi_get_min_amount(from_chain, from_token, to_token, amount)

        if amount_ >= min_amount_swap:
            contract_txn = contract.functions.swap(
                from_token,
                to_token,
                amount,
                minToAmount,
                wallet,
                wallet
            ).build_transaction(
                {
                    'from': wallet,
                    'nonce': web3.eth.get_transaction_count(wallet),
                    'value': value,
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            if from_chain == 'bsc':
                contract_txn['gasPrice'] = random.randint(1000000000, 1050000000) # специально ставим 1 гвей, так транза будет дешевле
            else:
                contract_txn = add_gas_price(web3, contract_txn)
            contract_txn = add_gas_limit(web3, contract_txn)

            if swap_all_balance:
                if from_token == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                    gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                    contract_txn['value'] = contract_txn['value'] - gas_gas

            tx_hash = sign_tx(web3, contract_txn, privatekey)
            tx_link = f'{DATA[from_chain]["scan"]}/{tx_hash}'

            status = check_status_tx(from_chain, tx_hash)
            if status == 1:
                logger.success(f'{module_str} | {tx_link}')
                list_send.append(f'{STR_DONE}{module_str}')
                time.sleep(3)

            else:
                logger.error(f'{module_str} | tx is failed | {tx_link}')
                retry += 1
                if retry < settings['RETRY']:
                    logger.info(f'try again | {wallet}')
                    time.sleep(3)
                    woofi_swap(privatekey, from_chain, from_token, to_token, swap_all_balance, amount_from, amount_to,
                               min_amount_swap, keep_value_from, keep_value_to, retry + 1)
                else:
                    list_send.append(f'{STR_CANCEL}{module_str}')

        else:
            logger.error(f"{module_str} : can't swap : {amount_} (amount) < {min_amount_swap} (min_amount_swap)")
            list_send.append(f'{STR_CANCEL}{module_str} : {amount_} < {min_amount_swap}')

    except Exception as error:
        logger.error(f'{module_str} | error : {error}')
        if retry < settings['RETRY']:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            woofi_swap(privatekey, from_chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')


def woofi(private_key):
    from_chain = settings['value_woofi']['from_chain']
    to_chain = settings['value_woofi']['to_chain']
    from_token = settings['value_woofi']['from_token']
    to_token = settings['value_woofi']['to_token']
    swap_all_balance = settings['value_woofi']['to_token']
    amount_from = settings['value_woofi']['amount_from']
    amount_to = settings['value_woofi']['amount_to']
    min_amount_swap = settings['value_woofi']['min_amount_swap']
    keep_value_from = settings['value_woofi']['keep_value_from']
    keep_value_to = settings['value_woofi']['keep_value_to']

    if from_chain == to_chain:
        woofi_swap(private_key, from_chain, from_token, to_token, swap_all_balance, amount_from, amount_to,
                   min_amount_swap, keep_value_from, keep_value_to)
    else:
        woofi_bridge(private_key, from_chain, to_chain, from_token, to_token, swap_all_balance, amount_from, amount_to,
                     min_amount_swap, keep_value_from, keep_value_to)


def exchange_withdraw(private_key, retry=0):
    try:

        cex = settings['withdraw_coins']['cex']
        chain = settings['withdraw_coins']['chain']
        symbol = settings['withdraw_coins']['symbol']
        amount_from = settings['withdraw_coins']['amount_from']
        amount_to = settings['withdraw_coins']['amount_to']
        amount_ = round(random.uniform(amount_from, amount_to), 7)

        API_KEY = settings['CEX_KEYS'][cex]['api_key']
        API_SECRET = settings['CEX_KEYS'][cex]['api_secret']

        wallet = evm_wallet(private_key)

        dict_ = {
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        }

        if cex in ['kucoin']:
            dict_['password'] = settings['CEX_KEYS'][cex]['password']

        account = ccxt.__dict__[cex](dict_)

        account.withdraw(
            code=symbol,
            amount=amount_,
            address=wallet,
            tag=None,
            params={
                "network": chain
            }
        )
        logger.success(f"{cex}_withdraw success => {wallet} | {amount_} {symbol}")
        list_send.append(f'{STR_DONE}{cex}_withdraw')

    except Exception as error:
        logger.error(f"{cex}_withdraw unsuccess => {wallet} | error : {error}")
        list_send.append(f'{STR_CANCEL}{cex}_withdraw')

