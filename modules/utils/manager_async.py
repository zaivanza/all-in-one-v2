from datas.data import DATA
from config import ERC20_ABI, max_time_check_tx_status, PRICES_NATIVE, WALLET_PROXIES
from setting import MAX_GAS_CHARGE, USE_PROXY, RETRY
from .helpers import sleeping, decimalToInt, round_to

import time
from loguru import logger
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import random
import asyncio

class Web3ManagerAsync:

    BSC_GAS_PRICE = 1000000000 # Intentionally setting 1 Gwei to make the transaction cheaper
    
    def __init__(self, key: str, chain: str):
        self.key = key
        self.chain = chain
        self.web3 = self._initialize_web3()
        self.address = self._get_account_address()
        self.chain_id = self._get_chain_id()

    def _initialize_web3(self) -> Web3:
        rpc = DATA[self.chain]['rpc']
        web3 = Web3(AsyncHTTPProvider(rpc), modules={"eth": (AsyncEth)}, middlewares=[])

        if (USE_PROXY and WALLET_PROXIES):
            try:
                proxy = WALLET_PROXIES[self.key]
                web3 = Web3(AsyncHTTPProvider(rpc, request_kwargs={"proxy": proxy}), modules={"eth": (AsyncEth)}, middlewares=[])
            except Exception as error:
                logger.error(f'{error}. Use web3 without proxy')
        return web3
    
    def _get_account_address(self) -> str:
        return self.web3.eth.account.from_key(self.key).address

    def _get_chain_id(self) -> int:
        return DATA[self.chain]['chain_id']

    async def add_gas_limit(self, contract_txn) -> dict:
        value = contract_txn['value']
        contract_txn['value'] = 0
        pluser = [1.02, 1.05]
        gasLimit = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))

        contract_txn['value'] = value
        return contract_txn

    async def add_gas_limit_layerzero(self, contract_txn) -> dict:
        pluser = [1.05, 1.07]
        gasLimit = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
        return contract_txn

    async def add_gas_price(self, contract_txn) -> dict:
        if self.chain == 'bsc':
            contract_txn['gasPrice'] = self.BSC_GAS_PRICE 
        else:
            gas_price = await self.web3.eth.gas_price
            contract_txn['gasPrice'] = int(gas_price * random.uniform(1.01, 1.02))
        return contract_txn

    async def get_data_token(self, token_address: str):
        try:
            token_contract  = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            decimals        = await token_contract.functions.decimals().call()
            symbol          = await token_contract.functions.symbol().call()
            return token_contract, decimals, symbol
        except Exception as error:
            logger.error(error)

    def get_total_fee(self, contract_txn) -> bool:
        gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
        gas = decimalToInt(gas, 18) * PRICES_NATIVE[self.chain]

        logger.info(f'total_gas : {round_to(gas)} $')
        if gas > MAX_GAS_CHARGE[self.chain]:
            logger.info(f'gas is too high : {round_to(gas)}$ > {MAX_GAS_CHARGE[self.chain]}$. sleep and try again')
            sleeping(30,30)
            return False
        else:
            return True

    async def sign_tx(self, contract_txn):
        signed_tx = self.web3.eth.account.sign_transaction(contract_txn, self.key)
        raw_tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        return tx_hash
    
    async def get_status_tx(self, tx_hash) -> int:
        logger.info(f'{self.chain} : checking tx_status : {tx_hash}')
        start_time_stamp = int(time.time())

        while True:
            try:
                receipt = await self.web3.eth.get_transaction_receipt(tx_hash)
                status = receipt["status"]
                if status in [0, 1]:
                    return status

            except:
                time_stamp = int(time.time())
                if time_stamp-start_time_stamp > max_time_check_tx_status:
                    logger.info(f'Did not receive tx_status for {max_time_check_tx_status} sec, assuming that tx is a success')
                    return 1
                await asyncio.sleep(1)

    async def send_tx(self, contract_txn):
        try:
            if contract_txn["value"] >= 0:
                tx_hash = await self.sign_tx(contract_txn)
                status  = await self.get_status_tx(tx_hash)
                tx_link = f'{DATA[self.chain]["scan"]}/{tx_hash}'
                return status, tx_link
            else: False, "Value less 0"
        except Exception as error:
            logger.error(error)
            return False, error

    async def get_amount_in(self, keep_from: float | int, keep_to: float | int, all_balance: bool, token: str, amount_from: float | int, amount_to: float | int, multiplier=1) -> float | int:
        keep_value = round(random.uniform(keep_from, keep_to), 8)
        if all_balance: amount = await self.get_balance(token) - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)

        amount = amount*multiplier
        return amount
    
    async def get_token_info(self, token_address: str) -> dict:
        if token_address == '': 
            address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            decimal = 18
            symbol = DATA[self.chain]['token']
            token_contract = ''
        else:
            address = Web3.to_checksum_address(token_address)
            token_contract, decimal, symbol = await self.get_data_token(address)

        return {'address': address, 'symbol': symbol, 'decimal': decimal, 'contract': token_contract}
    
    async def get_balance(self, token_address: str) -> float | int:
        while True:
            try:
                token_data = await self.get_token_info(token_address)
                if token_address == '': # eth
                    balance = await self.web3.eth.get_balance(self.web3.to_checksum_address(self.address))
                else:
                    balance = await token_data['contract'].functions.balanceOf(self.web3.to_checksum_address(self.address)).call()

                balance_human = decimalToInt(balance, token_data['decimal']) 
                return balance_human

            except Exception as error:
                logger.error(error)
                await asyncio.sleep(1)

    async def get_allowance(self, token_address: str, spender: str) -> int:
        try:
            contract  = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            amount_approved = await contract.functions.allowance(self.address, spender).call()
            return amount_approved
        except Exception as error:
            logger.error(f'{error}. Return 0')
            return 0

    async def approve(self, amount: int, token_address: str, spender: str, retry=0):
        try:
            spender = Web3.to_checksum_address(spender)
            token_data = await self.get_token_info(token_address)

            module_str = f'approve : {token_data["symbol"]}'

            allowance_amount = await self.get_allowance(token_address, spender)
            if amount <= allowance_amount: return

            contract_txn = await token_data["contract"].functions.approve(
                spender,
                115792089237316195423570985008687907853269984665640564039457584007913129639935
                ).build_transaction(
                {
                    "chainId": self.chain_id,
                    "from": self.address,
                    "nonce": await self.web3.eth.get_transaction_count(self.address),
                    'gasPrice': 0,
                    'gas': 0,
                    "value": 0
                }
            )

            contract_txn = await self.add_gas_price(contract_txn)
            contract_txn = await self.add_gas_limit(contract_txn)

            if self.get_total_fee(contract_txn) == False: return await self.approve(amount, token_address, spender, retry)

            status, tx_link = await self.send_tx(contract_txn)

            if status == 1:
                logger.success(f"{self.address} | {module_str} | {tx_link}")
                await asyncio.sleep(5)
            else:
                logger.error(f"{module_str} | tx is failed | {tx_link}")
                if retry < RETRY:
                    logger.info(f"try again in 10 sec.")
                    await asyncio.sleep(10)
                    return await self.approve(amount, token_address, spender, retry+1)

        except Exception as error:
            logger.error(f'{error}')
            if retry < RETRY:
                logger.info(f'try again in 10 sec.')
                await asyncio.sleep(10)
                return await self.approve(amount, token_address, spender, retry+1)

    async def wait_balance(self, number: str, min_balance: float | int, token_address: str):
        token_data = await self.get_token_info(token_address)
        logger.info(f'{number} {self.address} | waiting {min_balance} {token_data["symbol"]} [{self.chain}]')

        while True:
            try:
                balance = await self.get_balance(token_address)
                if balance > min_balance:
                    logger.info(f'{number} {self.address} | balance : {round_to(balance)} {token_data["symbol"]} [{self.chain}]')
                    break
                await asyncio.sleep(10)

            except Exception as error:
                logger.error(f'balance error : {error}. check again')
                await asyncio.sleep(10)
