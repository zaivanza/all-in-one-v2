from data.data import DATA
from setting import value_1inch_swap, RETRY
from config import STR_DONE, STR_CANCEL, PROXIES
from .helpers import get_web3, approve_, sign_tx, check_balance, check_data_token, check_status_tx, checker_total_fee, round_to, list_send, intToDecimal, sleeping

from loguru import logger
from web3 import Web3
import random, requests, time

def get_api_call_data(url):

    def try_get_with_proxy():
        try:
            proxy = random.choice(PROXIES)
            # cprint(proxy, 'yellow')
            proxies = {
                'http'  : proxy,
                'https' : proxy,
            }
            call_data = requests.get(url, proxies=proxies)
            return call_data
        except Exception as error:
            logger.error(error)
            call_data = requests.get(url)
            return call_data

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
                time.sleep(1)
                return get_api_call_data(url)

def inch_swap(privatekey, params, retry=0):

    try:

        module_str = '1inch_swap'
        logger.info(module_str)

        # base_url = 'https://api-defillama.1inch.io'
        base_url = 'https://api.1inch.io'
        inch_version = 5

        if params is not None:
            chain = params['chain']
            swap_all_balance = params['swap_all_balance']
            min_amount_swap = params['min_amount_swap']
            amount_from = params['amount_from']
            amount_to = params['amount_to']
            keep_value_from = params['keep_value_from']
            keep_value_to = params['keep_value_to']
            from_token_address = params['from_token_address']
            to_token_address = params['to_token_address']
            slippage = params['slippage']

        else:
            chain, swap_all_balance, min_amount_swap, keep_value_from, keep_value_to, amount_from, amount_to, from_token_address, to_token_address, slippage = value_1inch_swap()

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance == True: amount = check_balance(privatekey, chain, from_token_address) - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)

        web3 = get_web3(chain, privatekey)
        chain_id = web3.eth.chain_id

        if from_token_address == '': 
            from_token_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            from_decimals = 18
            from_symbol = DATA[chain]['token']
        else:
            from_token_contract, from_decimals, from_symbol = check_data_token(chain, from_token_address)

        if to_token_address   == '': 
            to_token_address   = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            to_symbol = DATA[chain]['token']
        else:
            to_token_contract, to_decimals, to_symbol = check_data_token(chain, to_token_address)

        account = web3.eth.account.from_key(privatekey)
        wallet  = account.address

        amount = amount*0.999
        amount_to_swap = intToDecimal(amount, from_decimals) 

        spender_json    = get_api_call_data(f'{base_url}/v{inch_version}.0/{chain_id}/approve/spender')
        spender         = Web3.to_checksum_address(spender_json['address'])

        # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апруваем
        if from_token_address != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            approve_(amount_to_swap, privatekey, chain, from_token_address, spender)

        _1inchurl = f'{base_url}/v{inch_version}.0/{chain_id}/swap?fromTokenAddress={from_token_address}&toTokenAddress={to_token_address}&amount={amount_to_swap}&fromAddress={wallet}&slippage={slippage}'
        json_data = get_api_call_data(_1inchurl)

        # cprint(json_data, 'blue')

        if json_data == False: 
            logger.info('failed to swap in 1inch')

        else:

            # cprint(json_data, 'yellow')

            tx  = json_data['tx']

            tx['chainId']   = chain_id
            tx['nonce']     = web3.eth.get_transaction_count(wallet)
            tx['to']        = Web3.to_checksum_address(tx['to'])
            tx['gasPrice']  = int(tx['gasPrice'])
            tx['gas']       = int(tx['gas'])
            tx['value']     = int(tx['value'])

            if chain == 'bsc':
                tx['gasPrice'] = random.randint(1000000000, 1050000000) # специально ставим 1 гвей, так транза будет дешевле

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(tx['gas'] * tx['gasPrice'])
            is_fee      = checker_total_fee(chain, total_fee)
            if is_fee   == False: return inch_swap(privatekey, params, retry)

            if amount >= min_amount_swap:

                tx_hash     = sign_tx(web3, tx, privatekey)
                tx_link     = f'{DATA[chain]["scan"]}/{tx_hash}'

                module_str = f'1inch_swap : {round_to(amount)} {from_symbol} => {to_symbol}'

                status  = check_status_tx(chain, tx_hash)

                if status == 1:
                    logger.success(f'{module_str} | {tx_link}')
                    list_send.append(f'{STR_DONE}{module_str}')
                    return "success"
                else:
                    logger.error(f'{module_str} | tx is failed | {tx_link}')
                    if retry < RETRY:
                        logger.info(f'try again in 10 sec.')
                        sleeping(10, 10)
                        inch_swap(privatekey, params, retry+1)

            else:
                logger.error(f"{module_str} : can't swap : {amount} (amount) < {min_amount_swap} (min_amount_swap)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} less {min_amount_swap}')

    except KeyError:
        logger.error(json_data['description'])
        module_str = '1inch_swap'
        list_send.append(f'{STR_CANCEL}{module_str}')

    except Exception as error:
        module_str = '1inch_swap'
        logger.error(f'{module_str} | error : {error}')
        if retry < RETRY:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            inch_swap(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')