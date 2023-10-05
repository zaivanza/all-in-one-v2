from config import WALLETS, STR_DONE, STR_CANCEL
from setting import RANDOMIZER, CHECK_GWEI, TG_BOT_SEND , IS_SLEEP, DELAY_SLEEP, RETRY, WALLETS_IN_BATCH, TRACK

from modules.utils.helpers import list_send, wait_gas, send_msg, async_sleeping
from modules.utils.manager_async import Web3ManagerAsync
from modules import *

from loguru import logger
from termcolor import cprint
import random
import asyncio

MODULES = {
    1: ("web3_checker", Web3Checker),
    2: ("debank_checker", DeBank),
    3: ("exchange_withdraw", ExchangeWithdraw),
    4: ("okx_withdraw", OkxWithdraw),
    5: ("transfer", Transfer),
    6: ("0x_swap", ZeroXswap),
    7: ("orbiter_bridge", OrbiterBridge),
    8: ("woofi_bridge", WoofiBridge), 
    9: ("woofi_swap", WoofiSwap), 
    10: ("sushiswap", SushiSwap),  
    11: ("bungee_refuel", BungeeRefuel),
    12: ("tx_checker", TxChecker),  
    13: ("1inch_swap", InchSwap),
    14: ("merkly_refuel", MerklyRefuel), 
    15: ("nft_checker", NFTChecker), 
}

def get_module(module):
    module_info = MODULES.get(module)
    if module_info:
        module_name, func = module_info
        # cprint(f'\nstart : {module_name}', 'white')
        return func, module_name
    else:
        raise ValueError(f"Unsupported module: {module}")

def is_private_key(value):
    return len(value) == 66 and value.startswith('0x')

async def worker(func, key, number):
    func_instance = func(key, number)
    await func_instance.setup()

    contract_txn = await func_instance.get_txn()
    if not contract_txn:
        logger.error(f'{number} {func_instance.manager.address} | error getting contract_txn')
        return False

    status, tx_link = await func_instance.manager.send_tx(contract_txn)

    if status == 1:
        logger.success(f'{number} {func_instance.manager.address} | {func_instance.module_str} | {tx_link}')
        list_send.append(f'{STR_DONE}{func_instance.module_str}')
        return True
    else:
        logger.error(f'{number} {func_instance.manager.address} | tx is failed | {tx_link}')
        return await retry_worker(func, key, number, retry=0)

async def retry_worker(func, key, number, retry):
    if retry < RETRY:
        logger.info(f'try again in 10 sec.')
        await asyncio.sleep(10)
        return await worker(func, key, number, retry+1)
    else:
        list_send.append(f'{STR_CANCEL}{func.module_str}')
        return False

async def process_exchanges(func, wallets):
    for key in wallets:
        exchange = func(key)
        res = await exchange.start()
        if (TG_BOT_SEND and len(list_send) > 0):
            send_msg()
        list_send.clear()
        if IS_SLEEP and res:
            time_sleep = random.randint(*DELAY_SLEEP)
            logger.info(f'sleep for {time_sleep} sec.')
            await asyncio.sleep(time_sleep)

async def process_batches(func, wallets):
    batches = [wallets[i:i + WALLETS_IN_BATCH] for i in range(0, len(wallets), WALLETS_IN_BATCH)]

    number = 0
    for batch in batches:
        if CHECK_GWEI:
            wait_gas()

        tasks = []
        for key in batch:
            number += 1
            if is_private_key(key):
                tasks.append(asyncio.create_task(worker(func, key, f'[{number}/{len(wallets)}]')))
            else:
                logger.error(f"{key} isn't private key")
        res = await asyncio.gather(*tasks)

        if (TG_BOT_SEND and len(list_send) > 0):
            send_msg()
        list_send.clear()

        if IS_SLEEP and any(res):
            await async_sleeping(*DELAY_SLEEP)

async def worker_tracks(key, number):

    for params in TRACK:
        if params['module_name'] == 'wait_balance':
            manager = Web3ManagerAsync(key, params['params']['chain'])
            await manager.wait_balance(number, params['params']['min_balance'], params['params']['token'])
        
        elif params['module_name'] == 'sleeping':
            time_sleep = random.randint(int(params['params']['from']), int(params['params']['to']))
            logger.info(f'sleep for {time_sleep} sec.')
            await asyncio.sleep(time_sleep)
        
        else:
    
            attempts = 0
            while attempts <= RETRY:
                func, module_name = get_module(int(params['module_number']))
                func_instance = func(key, number, params['params'])
                await func_instance.setup()
                logger.debug(f'{number} {func_instance.manager.address} : {module_name}')

                contract_txn = await func_instance.get_txn()
                if contract_txn:
                    status, tx_link = await func_instance.manager.send_tx(contract_txn)

                    if status == 1:
                        logger.success(f'{number} {func_instance.manager.address} | {func_instance.module_str} | {tx_link}')
                        list_send.append(f'{STR_DONE}{func_instance.module_str}')
                        break

                    else:
                        logger.error(f'{number} {func_instance.manager.address} | tx is failed | {tx_link}')
                        attempts += 1
                        logger.info('sleep for 10 sec.')
                        await asyncio.sleep(10)
                else:
                    attempts += 1
                    logger.error(f'{number} {func_instance.manager.address} | error getting contract_txn')
                    logger.info('sleep for 3 sec.')
                    await asyncio.sleep(3)

            else:
                logger.error(f'{number} {func_instance.manager.address} | module is not success, cycle broken')
                list_send.append(f'{STR_CANCEL}{func_instance.module_str}')
                break

async def main_tracks():

    if RANDOMIZER:
        random.shuffle(WALLETS)

    batches = [WALLETS[i:i + WALLETS_IN_BATCH] for i in range(0, len(WALLETS), WALLETS_IN_BATCH)]

    number = 0
    for batch in batches:
        if CHECK_GWEI:
            wait_gas()

        tasks = []
        for key in batch:
            if is_private_key(key):
                number += 1
                tasks.append(asyncio.create_task(worker_tracks(key, f'[{number}/{len(WALLETS)}]')))
            else:
                logger.error(f"{key} isn't private key")
        res = await asyncio.gather(*tasks)

        if (TG_BOT_SEND and len(list_send) > 0):
            send_msg()
        list_send.clear()

        if IS_SLEEP and any(res):
            await async_sleeping(*DELAY_SLEEP)

async def main(module):
    func, module_name = get_module(module)

    if RANDOMIZER:
        random.shuffle(WALLETS)

    if module in [1, 2, 12, 15]:
        await func().start()
    else:
        if module in [3, 4]:
            await process_exchanges(func, WALLETS)
        else:
            await process_batches(func, WALLETS)

