from data.data import DATA
from data.abi.abi import ABI_WOOFI_SWAP, ABI_WOOFI_BRIDGE
from config import STR_DONE, STR_CANCEL, WOOFI_SWAP_CONTRACTS, WOOFI_PATH, LAYERZERO_CHAINS_ID, WOOFI_BRIDGE_CONTRACTS
from setting import value_woofi_bridge, value_woofi_swap, RETRY
from .helpers import get_web3, add_gas_limit, add_gas_price, sign_tx, check_balance, approve_, check_data_token, check_status_tx, checker_total_fee, list_send, add_gas_limit_layerzero, decimalToInt, intToDecimal, sleeping

from loguru import logger
from web3 import Web3
import random, time
from termcolor import cprint

def woofi_get_min_amount(privatekey, chain, from_token, to_token, amount):

    try:

        if from_token.upper() != to_token.upper():

            # cprint(f'{chain} : {from_token} => {to_token} | {amount}', 'blue')

            slippage = 0.95

            web3 = get_web3(chain, privatekey)
            address_contract = web3.to_checksum_address(WOOFI_SWAP_CONTRACTS[chain])
            contract = web3.eth.contract(address=address_contract, abi=ABI_WOOFI_SWAP)

            from_token  = Web3.to_checksum_address(from_token)
            to_token    = Web3.to_checksum_address(to_token)

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

def woofi_bridge(privatekey, params, retry=0):

    try:

        if params is not None:
            from_chain = params['from_chain']
            to_chain = params['to_chain']
            from_token = params['from_token']
            to_token = params['to_token']
            swap_all_balance = params['swap_all_balance']
            amount_from = params['amount_from']
            amount_to = params['amount_to']
            min_amount_swap = params['min_amount_swap']
            keep_value_from = params['keep_value_from']
            keep_value_to = params['keep_value_to']
        else:
            from_chain, to_chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to = value_woofi_bridge()

        def get_srcInfos(amount_, from_chain, from_token):

            from_token = Web3.to_checksum_address(from_token)

            if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                token_contract, decimals, symbol = check_data_token(from_chain, from_token)
            else: decimals = 18

            amount = intToDecimal(amount_, decimals)
            bridgeToken = WOOFI_PATH[from_chain]
            minBridgeAmount = woofi_get_min_amount(privatekey, from_chain, from_token, WOOFI_PATH[from_chain], amount)

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

            chainId     = LAYERZERO_CHAINS_ID[to_chain]

            minToAmount = int(woofi_get_min_amount(privatekey, to_chain, WOOFI_PATH[to_chain], to_token, amount) * 0.99)
            bridgeToken = WOOFI_PATH[to_chain]

            bridgeToken = Web3.to_checksum_address(bridgeToken)
            to_token    = Web3.to_checksum_address(to_token)

            dstInfos = [
                chainId,
                to_token,       # toToken
                bridgeToken,    # bridgeToken
                minToAmount,    # minToAmount
                0               # airdropNativeAmount
            ]

            return dstInfos

        module_str = f'woofi_bridge : {from_chain} => {to_chain}'
        logger.info(module_str)

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance == True: amount_ = check_balance(privatekey, from_chain, from_token) - keep_value
        else: amount_ = round(random.uniform(amount_from, amount_to), 8)
            
        web3 = get_web3(from_chain, privatekey)
        address_contract = web3.to_checksum_address(
            WOOFI_BRIDGE_CONTRACTS[from_chain]
        )

        if from_token != '':
            token_contract, decimals, symbol = check_data_token(from_chain, from_token)
        else:
            decimals = 18

        contract    = web3.eth.contract(address=address_contract, abi=ABI_WOOFI_BRIDGE)
        wallet      = web3.eth.account.from_key(privatekey).address

        if to_token     == '' : to_token    = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        if from_token   == '' : from_token  = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        amount      = intToDecimal(amount_, decimals)
        srcInfos    = get_srcInfos(amount_, from_chain, from_token)

        if from_chain == 'bsc':
            amount_src = decimalToInt(srcInfos[3], 18)
            amount_src = intToDecimal(amount_src, 6)
        else:
            amount_src = srcInfos[3]

        dstInfos    = get_dstInfos(amount_src, to_chain, to_token)

        # cprint(f'\nsrcInfos : {srcInfos}\ndstInfos : {dstInfos}', 'blue')

        # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апруваем
        if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            approve_(amount, privatekey, from_chain, from_token, WOOFI_BRIDGE_CONTRACTS[from_chain])
            sleeping(5, 10)

        layerzero_fee = contract.functions.quoteLayerZeroFee(
            random.randint(112101680502565000, 712101680502565000), # refId
            wallet, # to
            srcInfos, 
            dstInfos
            ).call()
        layerzero_fee = int(layerzero_fee[0] * 1)

        if from_token == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            value = int(amount + layerzero_fee)
        else:
            value = int(layerzero_fee)

        if amount_ >= min_amount_swap:
            contract_txn = contract.functions.crossSwap(
                random.randint(112101680502565000, 712101680502565000), # refId
                wallet, # to
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

            if (from_token == '' and swap_all_balance == True):
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = int(contract_txn['value'] - gas_gas)

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'] + layerzero_fee)
            is_fee      = checker_total_fee(from_chain, total_fee)
            if is_fee   == False: return woofi_bridge(privatekey, params, retry)

            tx_hash = sign_tx(web3, contract_txn, privatekey)
            tx_link = f'{DATA[from_chain]["scan"]}/{tx_hash}'

            status = check_status_tx(from_chain, tx_hash)
            if status == 1:
                logger.success(f'{module_str} | {tx_link}')
                list_send.append(f'{STR_DONE}{module_str}')
                return "success"

            else:
                logger.error(f'{module_str} | tx is failed | {tx_link}')

                retry += 1
                if retry < RETRY:
                    logger.info(f'try again | {wallet}')
                    time.sleep(3)
                    woofi_bridge(privatekey, params, retry+1)
                else:
                    list_send.append(f'{STR_CANCEL}{module_str}')

        else:
            logger.error(f"{module_str} : can't bridge : {amount_} (amount) < {min_amount_swap} (min_amount_swap)")
            list_send.append(f'{STR_CANCEL}{module_str} : {amount_} less {min_amount_swap}')

    except Exception as error:
        logger.error(f'{module_str} | error : {error}')
        if retry < RETRY:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            woofi_bridge(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')

def woofi_swap(privatekey, params, retry=0):

    try:
        if params is not None:
            from_chain = params['chain']
            from_token = params['from_token']
            to_token = params['to_token']
            swap_all_balance = params['swap_all_balance']
            amount_from = params['amount_from']
            amount_to = params['amount_to']
            min_amount_swap = params['min_amount_swap']
            keep_value_from = params['keep_value_from']
            keep_value_to = params['keep_value_to']
        else:
            from_chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to = value_woofi_swap()

        module_str = f'woofi_swap : {from_chain}'
        logger.info(module_str)

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance == True: amount_ = check_balance(privatekey, from_chain, from_token) - keep_value
        else: amount_ = round(random.uniform(amount_from, amount_to), 8)
            
        web3 = get_web3(from_chain, privatekey)
        address_contract = web3.to_checksum_address(
            WOOFI_SWAP_CONTRACTS[from_chain]
        )

        if to_token     == '' : to_token    = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        if from_token   == '' : from_token  = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        from_token = Web3.to_checksum_address(from_token)
        to_token    = Web3.to_checksum_address(to_token)

        if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            token_contract, decimals, symbol = check_data_token(from_chain, from_token)
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

        minToAmount = woofi_get_min_amount(privatekey, from_chain, from_token, to_token, amount)

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

            if (from_token == '' and swap_all_balance == True):
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = contract_txn['value'] - gas_gas

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'])
            is_fee      = checker_total_fee(from_chain, total_fee)
            if is_fee   == False: return woofi_swap(privatekey, params, retry)

            tx_hash = sign_tx(web3, contract_txn, privatekey)
            tx_link = f'{DATA[from_chain]["scan"]}/{tx_hash}'

            status = check_status_tx(from_chain, tx_hash)
            if status == 1:
                logger.success(f'{module_str} | {tx_link}')
                list_send.append(f'{STR_DONE}{module_str}')
                return "success"

            else:
                logger.error(f'{module_str} | tx is failed | {tx_link}')
                retry += 1
                if retry < RETRY:
                    logger.info(f'try again | {wallet}')
                    time.sleep(3)
                    woofi_swap(privatekey, params, retry+1)
                else:
                    list_send.append(f'{STR_CANCEL}{module_str}')

        else:
            logger.error(f"{module_str} : can't swap : {amount_} (amount) < {min_amount_swap} (min_amount_swap)")
            list_send.append(f'{STR_CANCEL}{module_str} : {amount_} less {min_amount_swap}')

    except Exception as error:
        logger.error(f'{module_str} | error : {error}')
        if retry < RETRY:
            logger.info(f'try again in 10 sec.')
            sleeping(10, 10)
            woofi_swap(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')


