from data.data import DATA
from data.abi.abi import ABI_MERKLY_REFUEL
from config import STR_DONE, STR_CANCEL, MERKLY_CONTRACTS, LAYERZERO_CHAINS_ID, PRICES_NATIVE
from setting import value_merkly_refuel, RETRY
from .helpers import get_web3, add_gas_price, sign_tx, check_balance, add_gas_limit_layerzero, check_status_tx, checker_total_fee, list_send, intToDecimal, sleeping, decimalToInt, round_to, call_json

from loguru import logger
from web3 import Web3
import random
from eth_abi import encode
from termcolor import cprint
import sys

def get_adapterParams(gaslimit: int, amount: int):
    return Web3.to_hex(encode(["uint16", "uint64", "uint256"], [2, gaslimit, amount])[30:])

def check_merkly_fees():

    wallet = '0x7d4569a93937224bc4d6b679f25b899591efcccb' # рандомный кошелек

    result = {}

    for from_chain in MERKLY_CONTRACTS.items():
        from_chain = from_chain[0]

        result.update({from_chain:{}})

        web3 = Web3(Web3.HTTPProvider(DATA[from_chain]['rpc']))

        contract = web3.eth.contract(address=Web3.to_checksum_address(MERKLY_CONTRACTS[from_chain]), abi=ABI_MERKLY_REFUEL)
        adapterParams = get_adapterParams(250000, 1) + wallet[2:].lower()

        for to_chain in LAYERZERO_CHAINS_ID.items():
            to_chain = to_chain[0]

            if from_chain != to_chain:

                try:
                    send_value = contract.functions.estimateGasBridgeFee(LAYERZERO_CHAINS_ID[to_chain], False, adapterParams).call()
                    send_value = decimalToInt(send_value[0], 18)
                    send_value = round_to(send_value * PRICES_NATIVE[from_chain])
                    cprint(f'{from_chain} => {to_chain} : {send_value}', 'white')
                    result[from_chain].update({to_chain:send_value})
                except Exception as error:
                    cprint(f'{from_chain} => {to_chain} : None', 'white')
                    result[from_chain].update({to_chain:None})

    path = 'results/merkly_refuel'
    call_json(result, path)
    cprint(f'\nРезультаты записаны в {path}.json\n', 'blue')
    sys.exit()

def merkly_refuel(privatekey, params, retry=0):

    try:

        if params is not None:
            from_chain = params['from_chain']
            to_chain = params['to_chain']
            swap_all_balance = params['swap_all_balance']
            min_amount_swap = params['min_amount_swap']
            amount_from = params['amount_from']
            amount_to = params['amount_to']
            keep_value_from = params['keep_value_from']
            keep_value_to = params['keep_value_to']
            get_layerzero_fee = params['get_layerzero_fee']
        else:
            from_chain, to_chain, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to, get_layerzero_fee = value_merkly_refuel()

        if get_layerzero_fee == True:
            check_merkly_fees()
            return

        module_str = f'merkly_refuel : {from_chain} => {to_chain}'
        logger.info(module_str)

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance == True: amount = check_balance(privatekey, from_chain, '') - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)

        web3        = get_web3(from_chain, privatekey)
        account     = web3.eth.account.from_key(privatekey)
        wallet      = account.address

        contract = web3.eth.contract(address=Web3.to_checksum_address(MERKLY_CONTRACTS[from_chain]), abi=ABI_MERKLY_REFUEL)

        value = intToDecimal(amount, 18)
        adapterParams = get_adapterParams(250000, value) + wallet[2:].lower()
        send_value = contract.functions.estimateGasBridgeFee(LAYERZERO_CHAINS_ID[to_chain], False, adapterParams).call()

        contract_txn = contract.functions.bridgeGas(
                LAYERZERO_CHAINS_ID[to_chain],
                '0x0000000000000000000000000000000000000000', # _zroPaymentAddress
                adapterParams
            ).build_transaction(
            {
                "from": wallet,
                "value": send_value[0],
                "nonce": web3.eth.get_transaction_count(wallet),
                'gasPrice': 0,
                'gas': 0,
            }
        )

        if (amount > 0 and amount > min_amount_swap):

            if from_chain == 'bsc':
                contract_txn['gasPrice'] = 1000000000 # специально ставим 1 гвей, так транза будет дешевле
            else:
                contract_txn = add_gas_price(web3, contract_txn)

            contract_txn = add_gas_limit_layerzero(web3, contract_txn)

            if swap_all_balance == True:
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = int(contract_txn['value'] - gas_gas)

            # cprint(contract_txn, 'blue')

            # смотрим газ, если выше выставленного значения : спим
            total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'])
            is_fee      = checker_total_fee(from_chain, total_fee)
            if is_fee   == False: return merkly_refuel(privatekey, params, retry)

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
                    merkly_refuel(privatekey, params, retry+1)
                else:
                    logger.error(f'{module_str} | tx is failed | {tx_link}')
                    list_send.append(f'{STR_CANCEL}{module_str} | tx is failed | {tx_link}')

        else:
            logger.error(f"{module_str} : can't refuel : balance = {amount}")
            list_send.append(f"{STR_CANCEL}{module_str} : can't refuel : balance = {amount}")


    except Exception as error:
        logger.error(f'{module_str} | {error}')

        if retry < RETRY:
            logger.info(f'try again | {wallet}')
            sleeping(10, 10)
            merkly_refuel(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')

