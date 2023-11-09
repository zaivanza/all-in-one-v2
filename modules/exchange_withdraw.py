from datas.data import OKX_KEYS, CEX_KEYS, DATA
from config import STR_DONE, STR_CANCEL
from setting import Value_Exchange, Value_OKX, RETRY
from .utils.helpers import list_send, async_sleeping, round_to

from loguru import logger
import random, hmac, base64
import asyncio, aiohttp
import ccxt.async_support as ccxt
import datetime
from web3 import Web3

def get_address(key, is_private_key):
    if is_private_key:
        web3 = Web3(Web3.HTTPProvider(DATA["ethereum"]["rpc"]))
        try:
            address = web3.eth.account.from_key(key).address
        except Exception as error:
            logger.error(error)
            return ''
    else:
        address = key
    return address

class OkxWithdraw:

    def __init__(self, key, params=None):
        self.params = params
        if self.params:
            self.chain = self.params['chain']
            self.symbol = self.params['symbol']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.account = self.params['account']
            self.fee = self.params['fee']
            self.sub_acc = self.params['sub_acc']
            self.is_private_key = self.params['is_private_key']

        else:
            self.chain = Value_OKX.chain
            self.symbol = Value_OKX.symbol
            self.amount_from = Value_OKX.amount_from
            self.amount_to = Value_OKX.amount_to
            self.account = Value_OKX.account
            self.fee = Value_OKX.fee
            self.sub_acc = Value_OKX.sub_acc
            self.is_private_key = Value_OKX.is_private_key

        self.address = get_address(key, self.is_private_key)
        self.amount = round(random.uniform(self.amount_from, self.amount_to), 7)
        self.api_key = OKX_KEYS[self.account]['api_key']
        self.api_secret = OKX_KEYS[self.account]['api_secret']
        self.passphras = OKX_KEYS[self.account]['password']
        self.module_str = f"okx_withdraw : {round_to(self.amount)} {self.symbol} ({self.chain}) => {self.address}"

    async def make_http_request(self, url, method="GET", headers=None, params=None, data=None, timeout=10):
        async with aiohttp.ClientSession() as session:
            kwargs = {"url": url, "method": method, "timeout": timeout}
            
            if headers:
                kwargs["headers"] = headers
            
            if params:
                kwargs["params"] = params
            
            if data:
                kwargs["data"] = data
            
            async with session.request(**kwargs) as response:
                return await response.json()

    async def get_data(self, request_path="/api/v5/account/balance?ccy=USDT", body='', meth="GET"):

        def signature(
            timestamp: str, method: str, request_path: str, secret_key: str, body: str = ""
        ) -> str:
            if not body:
                body = ""

            message = timestamp + method.upper() + request_path + body
            mac = hmac.new(
                bytes(secret_key, encoding="utf-8"),
                bytes(message, encoding="utf-8"),
                digestmod="sha256",
            )
            d = mac.digest()
            return base64.b64encode(d).decode("utf-8")

        dt_now = datetime.datetime.utcnow()
        ms = str(dt_now.microsecond).zfill(6)[:3]
        timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, self.api_secret, body),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphras,
            'x-simulated-trading': '0'
        }

        return headers

    async def transfer_from_subaccounts(self):

        try:
            headers = await self.get_data(request_path="/api/v5/users/subaccount/list", meth="GET")
            list_sub = await self.make_http_request("https://www.okx.cab/api/v5/users/subaccount/list", headers=headers)

            for sub_data in list_sub['data']:
                name_sub = sub_data['subAcct']

                headers = await self.get_data(request_path=f"/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy={self.symbol}", meth="GET")
                sub_balance = await self.make_http_request(f"https://www.okx.cab/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy={self.symbol}", headers=headers)
                sub_balance = sub_balance['data'][0]['bal']

                logger.info(f'{name_sub} | sub_balance : {sub_balance} {self.symbol}')

                body = {"ccy": f"{self.symbol}", "amt": str(sub_balance), "from": 6, "to": 6, "type": "2", "subAcct": name_sub}
                headers = await self.get_data(request_path=f"/api/v5/asset/transfer", body=str(body), meth="POST")
                transfer = await self.make_http_request("https://www.okx.cab/api/v5/asset/transfer",data=str(body), method="POST", headers=headers)
                await asyncio.sleep(1)

        except Exception as error:
            logger.error(f'{error}. list_sub : {list_sub}')

    async def transfer_spot_to_funding(self):

        try:
            headers = await self.get_data(request_path=f"/api/v5/account/balance?ccy={self.symbol}")
            balance = await self.make_http_request(f'https://www.okx.cab/api/v5/account/balance?ccy={self.symbol}', headers=headers)
            balance = balance["data"][0]["details"][0]["cashBal"]

            if balance != 0:
                body = {"ccy": f"{self.symbol}", "amt": float(balance), "from": 18, "to": 6, "type": "0", "subAcct": "", "clientId": "", "loanTrans": "", "omitPosRisk": ""}
                headers = await self.get_data(request_path=f"/api/v5/asset/transfer", body=str(body), meth="POST")
                transfer = await self.make_http_request("https://www.okx.cab/api/v5/asset/transfer",data=str(body), method="POST", headers=headers)
        except Exception as ex:
            pass

    async def withdraw(self, retry=0):

        async def retry_attempt():
            logger.info(f"try again in 10 sec. => {self.address}")
            await async_sleeping(10, 10)
            return await self.withdraw(retry + 1)

        try:
            body = {"ccy":self.symbol, "amt":self.amount, "fee":self.fee, "dest":"4", "chain":f"{self.symbol}-{self.chain}", "toAddr":self.address}
            headers = await self.get_data(request_path=f"/api/v5/asset/withdrawal", meth="POST", body=str(body))
            result = await self.make_http_request("https://www.okx.cab/api/v5/asset/withdrawal",data=str(body), method="POST", headers=headers)

            if result['code'] == '0':
                logger.success(f"withdraw success => {self.address} | {self.amount} {self.symbol}")
                list_send.append(f'{STR_DONE}okx_withdraw | {self.amount} {self.symbol}')
                return True
            else:
                error = result['msg']
                logger.error(f"withdraw unsuccess => {self.address} | error : {error}")
                if retry < RETRY:
                    return await retry_attempt()
                else:
                    list_send.append(f"{STR_CANCEL}okx_withdraw :  {result['msg']}")
                    return False

        except Exception as error:
            logger.error(f"{self.module_str} | error : {error}")
            if retry < RETRY:
                return await retry_attempt()
            else:
                list_send.append(f'{STR_CANCEL}{self.module_str} | error : {error}')
                return False

    async def start(self):
        if self.sub_acc:
            await self.transfer_from_subaccounts()

        await self.transfer_spot_to_funding()
        return await self.withdraw()

class ExchangeWithdraw:

    def __init__(self, key, params=None):
        self.params = params
        if self.params:
            self.chain = self.params['chain']
            self.symbol = self.params['symbol']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.exchange = self.params['exchange']
            self.is_private_key = self.params['is_private_key']
        else:
            self.chain = Value_Exchange.chain
            self.symbol = Value_Exchange.symbol
            self.amount_from = Value_Exchange.amount_from
            self.amount_to = Value_Exchange.amount_to
            self.exchange = Value_Exchange.exchange
            self.is_private_key = Value_Exchange.is_private_key

        self.address = get_address(key, self.is_private_key)
        self.amount = round(random.uniform(self.amount_from, self.amount_to), 7)
        self.api_key = CEX_KEYS[self.exchange]['api_key']
        self.api_secret = CEX_KEYS[self.exchange]['api_secret']
        self.module_str = f"{self.exchange}_withdraw : {round_to(self.amount)} {self.symbol} ({self.chain}) => {self.address}"

    async def withdraw(self, retry=0):

        async def retry_attempt():
            logger.info(f"try again in 10 sec. => {self.address}")
            await async_sleeping(10, 10)
            return await self.withdraw(retry+1)

        dict_ = {
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        }

        if self.exchange in ['kucoin', 'bitget']:
            dict_['password'] = CEX_KEYS[self.exchange]['password']

        if self.exchange in ['bitget']:
            params = {"chain": self.chain}
        else:
            params = {"network": self.chain}

        account = ccxt.__dict__[self.exchange](dict_)

        try:

            await account.withdraw(
                code = self.symbol,
                amount = self.amount,
                address = self.address,
                tag = None, 
                params = params
            )
            logger.success(f"{self.exchange}_withdraw success => {self.address} | {self.amount} {self.symbol}")
            list_send.append(f'{STR_DONE}{self.exchange}_withdraw | {self.amount} {self.symbol}')
            await account.close()

            return True
    
        except Exception as error:
            await account.close()
            logger.error(f"{self.module_str} | error : {error}")
            if retry < RETRY:
                return await retry_attempt()
            else:
                list_send.append(f'{STR_CANCEL}{self.module_str} | error : {error}')
                return False

    async def start(self):
        return await self.withdraw()