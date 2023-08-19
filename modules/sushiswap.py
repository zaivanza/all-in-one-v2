from data.data import DATA
from data.abi.abi import ABI_SUSHISWAP
from config import STR_DONE, STR_CANCEL, SUSHISWAP_CONTRACTS, WETH_CONTRACTS
from setting import value_sushiswap, RETRY
from .helpers import get_web3, approve_, add_gas_price, sign_tx, check_balance, check_data_token, check_status_tx, checker_total_fee, round_to, list_send, intToDecimal, sleeping

from loguru import logger
from web3 import Web3
import random, requests, time

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

        url = f'https://{url_chains[chain]}api.0x.org/swap/v1/quote?buyToken={to_token}&sellToken={from_token}&sellAmount={value}&slippagePercentage={slippage/100}'
        
        response = requests.get(url)

        if response.status_code == 200:
            result = [response.json()]
            return result
        
        else:
            logger.error(f'response.status_code : {response.status_code}')
            return False
    
    except Exception as error:
        logger.error(error)
        return False

def get_sushi_amountOutMin(contract, value, from_token, to_token, slippage):

    contract_txn = contract.functions.getAmountsOut(
        value,
        [from_token, to_token],
        ).call()

    return int(contract_txn[1] * slippage)

def get_amountOut(chain, contract, value, from_token, to_token, slippage_, from_token_address, to_token_address):

    slippage = (1 - slippage_ / 100)

    if chain in ['nova']:
        amountOutMin    = get_sushi_amountOutMin(contract, value, from_token, to_token, slippage)
    else:

        if from_token_address == '':
            json_data = get_0x_quote(chain, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', to_token, value, slippage_)
        elif to_token_address == '':
            json_data = get_0x_quote(chain, from_token, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', value, slippage_)
        elif (to_token_address != '' and from_token_address != ''):
            json_data = get_0x_quote(chain, from_token, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', value, slippage_)

        if json_data != False:
            amountOutMin = int(int(json_data[0]['buyAmount']) * slippage)
        else:
            amountOutMin = get_sushi_amountOutMin(contract, value, from_token, to_token, slippage)

    return amountOutMin

def sushiswap(privatekey, params, retry=0):

    try:

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
            slippage_ = params['slippage']
        else:
            chain, from_token_address, to_token_address, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to, slippage_ = value_sushiswap()

        module_str = f'sushiswap ({chain})'
        logger.info(module_str)

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance == True: amount = check_balance(privatekey, chain, from_token_address) - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)

        web3        = get_web3(chain, privatekey)
        account     = web3.eth.account.from_key(privatekey)
        wallet      = account.address

        contract = web3.eth.contract(address=Web3.to_checksum_address(SUSHISWAP_CONTRACTS[chain]), abi=ABI_SUSHISWAP)

        # weth => token
        if from_token_address == '':

            from_token  = Web3.to_checksum_address(WETH_CONTRACTS[chain])
            to_token    = Web3.to_checksum_address(to_token_address)

            from_token_contract, from_token_decimal, from_symbol    = check_data_token(chain, from_token)
            to_token_contract, to_token_decimal, to_symbol          = check_data_token(chain, to_token)
            value = intToDecimal(amount, from_token_decimal)

            amountOutMin = get_amountOut(chain, contract, value, from_token, to_token, slippage_, from_token_address, to_token_address)

            contract_txn = contract.functions.swapExactETHForTokens(
                amountOutMin,
                [from_token, to_token],
                wallet, # receiver
                (int(time.time()) + 10000)  # deadline
                ).build_transaction(
                {
                    "from": wallet,
                    "value": value,
                    "nonce": web3.eth.get_transaction_count(wallet),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

        # token => weth
        if to_token_address == '':

            from_token  = Web3.to_checksum_address(from_token_address)
            to_token    = Web3.to_checksum_address(WETH_CONTRACTS[chain])

            from_token_contract, from_token_decimal, from_symbol    = check_data_token(chain, from_token)
            to_token_contract, to_token_decimal, to_symbol          = check_data_token(chain, to_token)
            value = intToDecimal(amount, from_token_decimal)

            amountOutMin = get_amountOut(chain, contract, value, from_token, to_token, slippage_, from_token_address, to_token_address)

            contract_txn = contract.functions.swapExactTokensForETH(
                value, # amountIn
                amountOutMin, # amountOutMin
                [from_token, to_token], # path
                wallet, # receiver
                (int(time.time()) + 10000)  # deadline
                ).build_transaction(
                {
                    "from": wallet,
                    "value": 0,
                    "nonce": web3.eth.get_transaction_count(wallet),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

        # token => token
        if (to_token_address != '' and from_token_address != ''):

            from_token  = Web3.to_checksum_address(from_token_address)
            to_token    = Web3.to_checksum_address(to_token_address)

            from_token_contract, from_token_decimal, from_symbol    = check_data_token(chain, from_token)
            to_token_contract, to_token_decimal, to_symbol          = check_data_token(chain, to_token)
            value = intToDecimal(amount, from_token_decimal)

            amountOutMin = get_amountOut(chain, contract, value, from_token, to_token, slippage_, from_token_address, to_token_address)

            contract_txn = contract.functions.swapExactTokensForTokens(
                value, # amountIn
                amountOutMin, # amountOutMin
                [from_token, to_token], # path
                wallet, # receiver
                (int(time.time()) + 10000)  # deadline
                ).build_transaction(
                {
                    "from": wallet,
                    "value": 0,
                    "nonce": web3.eth.get_transaction_count(wallet),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )


        if from_token_address != '': 
            approve_(value, privatekey, chain, from_token_address, SUSHISWAP_CONTRACTS[chain])

        if (amount > 0 and amount > min_amount_swap):

            contract_txn['nonce']   = web3.eth.get_transaction_count(wallet)
            contract_txn            = add_gas_price(web3, contract_txn)
            gasLimit                = web3.eth.estimate_gas(contract_txn)
            contract_txn['gas']     = int(gasLimit * random.uniform(1.03, 1.05))
            # contract_txn = add_gas_limit(web3, contract_txn)

            if chain == 'bsc':
                contract_txn['gasPrice'] = random.randint(1000000000, 1050000000) # специально ставим 1 гвей, так транза будет дешевле

            if (from_token_address == '' and swap_all_balance == True):
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = int(value) - int(gas_gas)

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'])
            is_fee      = checker_total_fee(chain, total_fee)
            if is_fee   == False: return sushiswap(privatekey, params, retry)

            tx_hash = sign_tx(web3, contract_txn, privatekey)
            tx_link = f'{DATA[chain]["scan"]}/{tx_hash}'

            status = check_status_tx(chain, tx_hash)
            if status == 1:
                logger.success(f'{module_str} : {round_to(amount)} {from_symbol} => {to_symbol} | {tx_link}')
                list_send.append(f'{STR_DONE}{module_str} : {round_to(amount)} {from_symbol} => {to_symbol}')
                return "success"

            else:
                if retry < RETRY:
                    logger.info(f'{module_str} | tx is failed, try again in 10 sec | {tx_link}')
                    sleeping(10, 10)
                    sushiswap(privatekey, params, retry+1)
                else:
                    logger.error(f'{module_str} | tx is failed | {tx_link}')
                    list_send.append(f'{STR_CANCEL}{module_str} | tx is failed | {tx_link}')

        else:
            logger.error(f"{module_str} : can't swap : balance = {amount}")
            list_send.append(f"{STR_CANCEL}{module_str} : can't swap : balance = {amount}")


    except Exception as error:
        logger.error(f'{module_str} | {error}')

        if retry < RETRY:
            logger.info(f'try again | {wallet}')
            sleeping(10, 10)
            sushiswap(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')


