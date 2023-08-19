from data.data import DATA
from data.abi.abi import ABI_BUNGEE_REFUEL
from config import BUNGEE_LIMITS, STR_DONE, STR_CANCEL, BUNGEE_REFUEL_CONTRACTS
from setting import value_bungee, RETRY
from .helpers import  add_gas_limit, add_gas_price, sign_tx, check_balance, check_status_tx, checker_total_fee, round_to, list_send, decimalToInt, intToDecimal, sleeping

from loguru import logger
from web3 import Web3
import random

def get_bungee_limits(from_chain, to_chain):

    from_chain_id   = DATA[from_chain]['chain_id']
    to_chain_id     = DATA[to_chain]['chain_id']

    data = BUNGEE_LIMITS

    for i in range(len(data['result'])):
        if data['result'][i]['chainId'] == from_chain_id:
            infos = data['result'][i]['limits']
            
            try:

                if  [x for x in infos if x['chainId'] == to_chain_id][0] \
                and [x for x in infos if x['chainId'] == to_chain_id][0]['isEnabled'] == True:
                    
                    info = [x for x in infos if x['chainId'] == to_chain_id][0]
                    return int(info['minAmount']), int(info['maxAmount'])
                else:
                    logger.error(f'рефуел из {from_chain} в {to_chain} невозможен')
                    return 0, 0

            except Exception as error:
                logger.error(error)

def bungee_refuel(privatekey, params, retry=0):

    try:

        if params is not None:
            from_chain = params['from_chain']
            to_chain = params['to_chain']
            bridge_all_balance = params['bridge_all_balance']
            amount_from = params['amount_from']
            amount_to = params['amount_to']
            min_amount_bridge = params['min_amount_bridge']
            keep_value_from = params['keep_value_from']
            keep_value_to = params['keep_value_to']

        else:
            from_chain, to_chain, bridge_all_balance, amount_from, amount_to, min_amount_bridge, keep_value_from, keep_value_to = value_bungee()

        module_str = f'bungee_refuel : {from_chain} => {to_chain}'
        logger.info(module_str)

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if bridge_all_balance == True: amount = check_balance(privatekey, from_chain, '') - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)

        limits      = get_bungee_limits(from_chain, to_chain)
        min_limit   = round_to(decimalToInt(limits[0], 18))
        max_limit   = round_to(decimalToInt(limits[1], 18))

        value       = intToDecimal(amount, 18)
        web3        = Web3(Web3.HTTPProvider(DATA[from_chain]['rpc']))
        account     = web3.eth.account.from_key(privatekey)
        wallet      = account.address

        if amount > min_limit and amount < max_limit: None
        else: 
            logger.error(f'amount {amount} but bungee_limits : {min_limit} - {max_limit}')
            list_send.append(f'{STR_CANCEL}{module_str} : amount {amount} but bungee_limits : {min_limit} - {max_limit}')
            return False

        if amount >= min_amount_bridge:

            contract = web3.eth.contract(address=Web3.to_checksum_address(BUNGEE_REFUEL_CONTRACTS[from_chain]), abi=ABI_BUNGEE_REFUEL)

            contract_txn = contract.functions.depositNativeToken(
                DATA[to_chain]['chain_id'],   # destinationChainId
                wallet                        # _to
                ).build_transaction(
                {
                    # "chainId": web3.eth.chain_id,
                    "from": wallet,
                    "nonce": web3.eth.get_transaction_count(wallet),
                    'gasPrice': 0,
                    'gas': 0,
                    "value": value
                }
            )

            contract_txn = add_gas_price(web3, contract_txn)
            contract_txn = add_gas_limit(web3, contract_txn)

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'])
            is_fee      = checker_total_fee(from_chain, total_fee)

            if is_fee == True:
                
                if bridge_all_balance == True:
                    gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                    contract_txn['value'] = contract_txn['value'] - gas_gas
                
                tx_hash = sign_tx(web3, contract_txn, privatekey)
                tx_link = f'{DATA[from_chain]["scan"]}/{tx_hash}'

                status = check_status_tx(from_chain, tx_hash)
                if status == 1:
                    logger.success(f'{module_str} | {tx_link}')
                    list_send.append(f'{STR_DONE}{module_str}')
                    return "success"

                else:
                    if retry < RETRY:
                        logger.info(f'{module_str} | tx is failed, try again in 10 sec | {tx_link}')
                        sleeping(10, 10)
                        bungee_refuel(privatekey,  params,retry+1)
                    else:
                        logger.error(f'{module_str} | tx is failed | {tx_link}')
                        list_send.append(f'{STR_CANCEL}{module_str} | tx is failed | {tx_link}')

            else:
                bungee_refuel(privatekey, params, retry)

        else:
            logger.error(f"{module_str} : can't bridge : {amount} (amount) < {min_amount_bridge} (min_amount_bridge)")
            list_send.append(f'{STR_CANCEL}{module_str} : {amount} less {min_amount_bridge}')


    except Exception as error:

        logger.error(f'{module_str} | {error}')
        if retry < RETRY:
            logger.info(f'try again | {wallet}')
            sleeping(10, 10)
            bungee_refuel(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')



