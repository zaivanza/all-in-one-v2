from data.data import DATA, API_0x
from setting import value_0x_swap, RETRY
from config import STR_DONE, STR_CANCEL
from .helpers import get_web3, approve_, sign_tx, check_balance, check_data_token, check_status_tx, checker_total_fee, round_to, list_send, intToDecimal, sleeping

from loguru import logger
from web3 import Web3
import random, requests

def get_0x_quote(chain, from_token, to_token, value, slippage):

    try:

        url_chains = {
            'ethereum'  : '',
            'bsc'       : 'bsc.',
            'arbitrum'  : 'arbitrum.',
            'optimism'  : 'optimism.',
            'polygon'   : 'polygon.',
            'fantom'    : 'fantom.',
            'avalanche' : 'avalanche.',
            'celo'      : 'celo.',
        }

        url     = f'https://{url_chains[chain]}api.0x.org/swap/v1/quote?buyToken={to_token}&sellToken={from_token}&sellAmount={value}&slippagePercentage={slippage/100}'
        header  = {'0x-api-key' : API_0x}
        
        response = requests.get(url, headers=header)

        if response.status_code == 200:
            result = [response.json()]
            return result
        
        else:
            logger.error(f'response.status_code : {response.status_code}')
            return False
    
    except Exception as error:
        logger.error(error)
        return False

def zeroX_swap(privatekey, params, retry=0):
        
    try:

        module_str = '0x_swap'
        logger.info(module_str)

        if params is not None:
            chain = params['chain']
            from_token_address = params['from_token_address']
            to_token_address = params['to_token_address']
            swap_all_balance = params['swap_all_balance']
            amount_from = params['amount_from']
            amount_to = params['amount_to']
            min_amount_swap = params['min_amount_swap']
            keep_value_from = params['keep_value_from']
            keep_value_to = params['keep_value_to']
            slippage = params['slippage']
        else:
            chain, swap_all_balance, min_amount_swap, keep_value_from, keep_value_to, amount_from, amount_to, from_token_address, to_token_address, slippage = value_0x_swap()

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance == True: amount = check_balance(privatekey, chain, from_token_address) - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)

        web3 = get_web3(chain, privatekey)

        if from_token_address == '': 
            from_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            from_decimals = 18
            from_symbol = DATA[chain]['token']
        else:
            from_token = from_token_address
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

        json_data = get_0x_quote(chain, from_token, to_token_address, amount_to_swap, slippage)

        if json_data != False:

            spender = json_data[0]['allowanceTarget']

            # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апрув
            if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                approve_(amount_to_swap, privatekey, chain, from_token_address, spender)

            contract_txn = {
                'from'      : wallet,
                'chainId'   : web3.eth.chain_id,
                'gasPrice'  : int(json_data[0]['gasPrice']),
                'nonce'     : web3.eth.get_transaction_count(wallet),
                'gas'       : int(json_data[0]['gas']),
                'to'        : Web3.to_checksum_address(json_data[0]['to']),
                'data'      : json_data[0]['data'],
                'value'     : int(json_data[0]['value']),
            }

            contract_txn['gas'] = int(contract_txn['gas'] * 1.5)

            if (from_token_address == '' and swap_all_balance == True):
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = int(int(amount_to_swap - gas_gas) * 0.999)

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'])
            is_fee      = checker_total_fee(chain, total_fee)
            if is_fee   == False: return zeroX_swap(privatekey, params, retry)

            if amount >= min_amount_swap:
                    
                tx_hash     = sign_tx(web3, contract_txn, privatekey)
                tx_link     = f'{DATA[chain]["scan"]}/{tx_hash}'

                module_str = f'0x_swap : {round_to(amount)} {from_symbol} => {to_symbol}'

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
                        zeroX_swap(privatekey, params, retry+1)

            else:
                logger.error(f"{module_str} : can't swap : {amount} (amount) < {min_amount_swap} (min_amount_swap)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} less {min_amount_swap}')

        else:
            list_send.append(f'{STR_CANCEL}{module_str}')

    except Exception as error:
        module_str = f'0x_swap'
        logger.error(f'{module_str} | error : {error}')
        if retry < RETRY:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            zeroX_swap(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')
