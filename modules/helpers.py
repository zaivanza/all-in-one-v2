from data.data import DATA, TG_TOKEN, TG_ID
from config import ERC20_ABI, max_time_check_tx_status, PRICES_NATIVE, WALLET_PROXIES
from setting import MAX_GWEI, MAX_GAS_CHARGE, USE_PROXY, RETRY

import time, json, requests
from loguru import logger
from web3 import Web3
import random
import telebot
import math
from tqdm import tqdm


list_send = []
def send_msg():

    try:
        str_send = '\n'.join(list_send)
        bot = telebot.TeleBot(TG_TOKEN)
        bot.send_message(TG_ID, str_send, parse_mode='html')  

    except Exception as error: 
        logger.error(error)

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

def check_data_token(chain, token_address):

    try:

        web3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        token_contract  = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        decimals        = token_contract.functions.decimals().call()
        symbol          = token_contract.functions.symbol().call()

        data = {
            'contract'  : token_contract,
            'decimal'   : decimals,
            'symbol'    : symbol
        }

        return token_contract, decimals, symbol
    
    except Exception as error:
        logger.error(error)

def check_status_tx(chain, tx_hash):

    logger.info(f'{chain} : checking tx_status : {tx_hash}')

    start_time_stamp = int(time.time())

    while True:
        try:

            rpc_chain   = DATA[chain]['rpc']
            web3        = Web3(Web3.HTTPProvider(rpc_chain))
            status_     = web3.eth.get_transaction_receipt(tx_hash)
            status      = status_["status"]

            if status in [0, 1]:
                return status

        except Exception as error:
            # logger.info(f'error, try again : {error}')
            time_stamp = int(time.time())
            if time_stamp-start_time_stamp > max_time_check_tx_status:
                logger.info(f'не получили tx_status за {max_time_check_tx_status} sec, думаем что tx is success')
                return 1
            time.sleep(1)

def add_gas_limit(web3, contract_txn):

    value = contract_txn['value']
    contract_txn['value'] = 0
    pluser = [1.02, 1.05]
    gasLimit = web3.eth.estimate_gas(contract_txn)
    contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))

    contract_txn['value'] = value
    return contract_txn

def add_gas_limit_layerzero(web3, contract_txn):

    pluser = [1.05, 1.07]
    gasLimit = web3.eth.estimate_gas(contract_txn)
    contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
    return contract_txn

def add_gas_price(web3, contract_txn):

    gas_price = web3.eth.gas_price
    contract_txn['gasPrice'] = int(gas_price * random.uniform(1.01, 1.02))
    return contract_txn

def round_to(num, digits=3):
    try:
        if num == 0: return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits: scale = digits
        return round(num, scale)
    except: return num

def check_balance(privatekey, chain, address_contract):
    try:

        web3 = get_web3(chain, privatekey)

        try     : wallet = web3.eth.account.from_key(privatekey).address
        except  : wallet = privatekey
            
        if address_contract == '': # eth
            balance         = web3.eth.get_balance(web3.to_checksum_address(wallet))
            token_decimal   = 18
        else:
            token_contract, token_decimal, symbol = check_data_token(chain, address_contract)
            balance = token_contract.functions.balanceOf(web3.to_checksum_address(wallet)).call()

        human_readable = decimalToInt(balance, token_decimal) 
        return human_readable

    except Exception as error:
        logger.error(error)
        time.sleep(1)
        check_balance(privatekey, chain, address_contract)

def check_allowance(chain, token_address, wallet, spender):

    try:
        web3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        contract  = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        amount_approved = contract.functions.allowance(wallet, spender).call()
        return amount_approved
    except Exception as error:
        logger.error(error)

def get_base_gas():

    try:

        web3 = Web3(Web3.HTTPProvider(DATA['ethereum']['rpc']))
        gas_price = web3.eth.gas_price
        gwei_gas_price = web3.from_wei(gas_price, 'gwei')

        return gwei_gas_price
    
    except Exception as error: 
        logger.error(error)
        return get_base_gas()

def wait_gas():

    logger.info(f'check gas')
    while True:

        current_gas = get_base_gas()

        if current_gas > MAX_GWEI:
            logger.info(f'current_gas : {current_gas} > {MAX_GWEI}')
            time.sleep(60)
        else: break

def checker_total_fee(chain, gas):

    gas = decimalToInt(gas, 18) * PRICES_NATIVE[chain]

    # cprint(f'total_gas : {round_to(gas)} $', 'blue')
    logger.info(f'total_gas : {round_to(gas)} $')

    if gas > MAX_GAS_CHARGE[chain]:
        logger.info(f'gas is too high : {round_to(gas)}$ > {MAX_GAS_CHARGE[chain]}$. sleep and try again')
        sleeping(30,30)
        return False
    else:
        return True
    
def get_web3(chain, wallet):

    rpc = DATA[chain]['rpc']

    if USE_PROXY == True:
        try:
            proxy = WALLET_PROXIES[wallet]
            web3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"proxies":{'https' : proxy, 'http' : proxy}}))
        except Exception as error:
            logger.error(f'{error}. Use web3 without proxy')
            web3 = Web3(Web3.HTTPProvider(rpc))

    else:
        web3 = Web3(Web3.HTTPProvider(rpc))

    return web3

def approve_(amount, privatekey, chain, token_address, spender, retry=0):

    try:

        logger.info('approve')

        web3 = get_web3(chain, privatekey)
        # web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        spender = Web3.to_checksum_address(spender)

        wallet = web3.eth.account.from_key(privatekey).address
        contract, decimals, symbol = check_data_token(chain, token_address)

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

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'])
            is_fee      = checker_total_fee(chain, total_fee)
            if is_fee   == False: return approve_(amount, privatekey, chain, token_address, spender, retry)

            tx_hash = sign_tx(web3, contract_txn, privatekey)
            tx_link = f'{DATA[chain]["scan"]}/{tx_hash}'

            status = check_status_tx(chain, tx_hash)

            if status == 1:
                logger.success(f"{module_str} | {tx_link}")
                sleeping(5, 5)
            else:
                logger.error(f"{module_str} | tx is failed | {tx_link}")
                if retry < RETRY:
                    logger.info(f"try again in 10 sec.")
                    sleeping(10, 10)
                    approve_(amount, privatekey, chain, token_address, spender, retry+1)

    except Exception as error:
        logger.error(f'{error}')
        if retry < RETRY:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            approve_(amount, privatekey, chain, token_address, spender, retry+1)

# разбивка массива на части по кол-ву элементов
def func_chunks_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]

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

def get_wallet_proxies(wallets, proxies):
    try:
        result = {}
        for i in range(len(wallets)):
            result[wallets[i]] = proxies[i % len(proxies)]
        return result
    except: None

def get_prices():

    try:

        prices = {
                'ETH': 0, 'BNB': 0, 'AVAX': 0, 'MATIC': 0, 'FTM': 0, 'xDAI': 0, 'CELO': 0, 'CORE': 0, 'ONE': 0
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
                'celo'          : prices['CELO'], 
                'polygon_zkevm' : prices['ETH'], 
                'core'          : prices['CORE'], 
                'harmony'       : prices['ONE'], 
            }

        return data
    
    except Exception as error:
        logger.error(f'{error}. Try again')
        time.sleep(1)
        return get_prices()
    
def wait_balance(privatekey, chain, min_balance, token):

    if token == '':
        symbol = DATA[chain]['token']
    else:
        token_contract, token_decimal, symbol = check_data_token(chain, token)

    logger.info(f'waiting {min_balance} {symbol} in {chain}')

    while True:

        try:
            balance = check_balance(privatekey, chain, token)

            if balance > min_balance:
                logger.info(f'balance : {balance}')
                break
            time.sleep(10)

        except Exception as error:
            logger.error(f'balance error : {error}. check again')
            sleeping(10,10)

