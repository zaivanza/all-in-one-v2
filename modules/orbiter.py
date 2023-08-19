from data.data import DATA
from data.abi.abi import ABI_ORBITER_TO_STARKNET
from config import ORBITER_MAKER, \
    STR_DONE, \
    STR_CANCEL, \
    ORBITER_AMOUNT, \
    ORBITER_AMOUNT_STR, \
    STARKNET_WALLETS, \
    CONTRACTS_ORBITER_TO_STARKNET
from setting import value_orbiter, RETRY
from .helpers import get_web3, add_gas_limit, add_gas_price, sign_tx, check_balance, check_status_tx, checker_total_fee, list_send, intToDecimal, sleeping

from loguru import logger
from web3 import Web3
import random, decimal

def check_orbiter_limits(from_chain, to_chain):

    orbiter_ids = {
        'ethereum'      : '1',
        'optimism'      : '7',
        'bsc'           : '15',
        'arbitrum'      : '2',
        'nova'          : '16',
        'polygon'       : '6',
        'polygon_zkevm' : '17',
        'zksync'        : '14',
        'zksync_lite'   : '3',
        'starknet'      : '4',
        'linea'         : '23',
        'base'          : '21',
        'mantle'        : '24',
    }

    from_maker  = orbiter_ids[from_chain]
    to_maker    = orbiter_ids[to_chain]

    maker_x_maker = f'{from_maker}-{to_maker}'

    for maker in ORBITER_MAKER:

        if maker_x_maker == maker:
            
            min_bridge  = ORBITER_MAKER[maker]['ETH-ETH']['minPrice']
            max_bridge  = ORBITER_MAKER[maker]['ETH-ETH']['maxPrice']
            fees        = ORBITER_MAKER[maker]['ETH-ETH']['tradingFee']

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

def orbiter_bridge(privatekey, params, retry=0):

    try:

        if params is not None:
            from_chain = params['from_chain']
            to_chain = params['to_chain']
            bridge_all_balance = params['bridge_all_balance']
            min_amount_bridge = params['min_amount_bridge']
            amount_from = params['amount_from']
            amount_to = params['amount_to']
            keep_value_from = params['keep_value_from']
            keep_value_to = params['keep_value_to']
        else:
            from_chain, to_chain, bridge_all_balance, amount_from, amount_to, min_amount_bridge, keep_value_from, keep_value_to = value_orbiter()

        module_str = f'orbiter_bridge : {from_chain} => {to_chain}'
        logger.info(module_str)

        min_bridge, max_bridge, fees = check_orbiter_limits(from_chain, to_chain)
        min_bridge = min_bridge + fees

        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if bridge_all_balance == True: amount = check_balance(privatekey, from_chain, '') - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)
        amount_to_bridge = amount 

        amount  = get_orbiter_value(amount_to_bridge, to_chain) # получаем нужный amount

        if (amount > min_bridge and amount < max_bridge):

            # cprint(amount, 'yellow')
            value   = intToDecimal(amount, 18)

            web3        = get_web3(from_chain, privatekey)
            account     = web3.eth.account.from_key(privatekey)
            wallet      = account.address
            chain_id    = web3.eth.chain_id
            nonce       = web3.eth.get_transaction_count(wallet)

            if amount >= min_amount_bridge:

                if to_chain == 'starknet':

                    starknet_address = STARKNET_WALLETS[privatekey]
                    if starknet_address[:3] == '0x0': starknet_wallet = f'030{starknet_address[3:]}'
                    else                            : starknet_wallet = f'030{starknet_address[2:]}'

                    starknet_wallet = bytes.fromhex(starknet_wallet) 

                    contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACTS_ORBITER_TO_STARKNET[from_chain]), abi=ABI_ORBITER_TO_STARKNET)

                    contract_txn = contract.functions.transfer(
                            '0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8', # _to
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
                        "from": wallet,
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

                # смотрим газ, если выше выставленного значения : спим
                total_fee   = int(contract_txn['gas'] * contract_txn['gasPrice'])
                is_fee      = checker_total_fee(from_chain, total_fee)
                if is_fee   == False: return orbiter_bridge(privatekey, params, retry)

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
                        orbiter_bridge(privatekey, params, retry+1)
                    else:
                        logger.error(f'{module_str} | tx is failed | {tx_link}')
                        list_send.append(f'{STR_CANCEL}{module_str} | tx is failed | {tx_link}')

            else:
                logger.error(f"{module_str} : can't bridge : {amount} (amount) < {min_amount_bridge} (min_amount_bridge)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} less {min_amount_bridge}')

        else:

            if amount < min_bridge:

                logger.error(f"{module_str} : can't bridge : {amount} (amount) < {min_bridge} (min_bridge)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} less {min_bridge}')

            elif amount > max_bridge:

                logger.error(f"{module_str} : can't bridge : {amount} (amount) > {max_bridge} (max_bridge)")
                list_send.append(f'{STR_CANCEL}{module_str} : {amount} over {max_bridge}')

    except Exception as error:

        logger.error(f'{module_str} | {error}')
        if retry < RETRY:
            logger.info(f'try again | {wallet}')
            sleeping(10, 10)
            orbiter_bridge(privatekey, params, retry+1)
        else:
            list_send.append(f'{STR_CANCEL}{module_str}')


