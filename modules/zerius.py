from datas.data import DATA
from .utils.contracts.abi import ABI_ZERIUS
from .utils.contracts.contract import ZERO_ADDRESS, ZERIUS_SEND_GAS_LIMIT, ZERIUS_CONTRACTS, ZERIUS_MINT_GAS_LIMIT, LAYERZERO_CHAINS_ID, EXCLUDED_LZ_PAIRS, COINGECKO_URL, LZ_CHAIN_TO_TOKEN

from config import STR_DONE, STR_CANCEL, WALLETS
from setting import Value_Zerius_ONFT, RETRY, WALLETS_IN_BATCH, CHECK_GWEI, TG_BOT_SEND, IS_SLEEP, DELAY_SLEEP, RANDOMIZER

from loguru import logger
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import random
import requests
import asyncio
from eth_account import Account
from decimal import *
from eth_abi.packed import encode_packed
from termcolor import cprint
import csv
from tabulate import tabulate

from .utils.manager_async import Web3ManagerAsync
from .utils.helpers import list_send, send_msg, round_to, wait_gas, is_private_key, async_sleeping

async def get_contract(chain):
    web3 = Web3(AsyncHTTPProvider(DATA[chain]['rpc']), modules={"eth": (AsyncEth)}, middlewares=[])
    return web3.eth.contract(address=Web3.to_checksum_address(ZERIUS_CONTRACTS[chain]), abi=ABI_ZERIUS)

async def get_balance_nfts_amount(contract, owner):
    return await contract.functions.balanceOf(Web3.to_checksum_address(owner)).call()

async def get_balance_nfts_id(contract, owner, i):
    return await contract.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(owner), i).call()

class Mint:
    def __init__(self, key, number, chains) -> None:
        self.key = key
        self.number = number
        self.chain = random.choice(chains)
        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.module_str = f'{self.number} {self.manager.address} | mint nft ({self.chain})'

    async def get_txn(self):
        try:
            self.contract = await get_contract(self.chain)
            mint_fee = await self.contract.functions.mintFee().call()

            contract_txn = await self.contract.functions.mint().build_transaction(
                {
                    "from": self.manager.address,
                    "value": mint_fee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)
            return contract_txn
            
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} | {error}')
            return False

class Bridge:
    def __init__(self, key, number, from_chain, to_chain, token_id, manager, module_str, contract) -> None:
        self.key = key
        self.number = number
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.token_id = token_id
        self.manager = manager
        self.module_str = module_str
        self.contract = contract

    async def estimateSendFee(
            self,
            toDstLzChainId: int,
            token_id: int, 
            toDstAddress: str,
            useZro: bool,
            adapterParams: bytes
        ) -> (int, int):
        return await self.contract.functions.estimateSendFee(
            toDstLzChainId,
            toDstAddress,
            token_id,
            useZro,
            adapterParams
        ).call()
    
    async def get_min_dst_gas_lookup(self, dstChainId, funcType):
        return await self.contract.functions.minDstGasLookup(dstChainId, funcType).call()

    async def get_txn(self):
        # try:
            adapterParams = encode_packed(
                ["uint16", "uint256"],
                [1, await self.get_min_dst_gas_lookup(LAYERZERO_CHAINS_ID[self.to_chain], 1)] # lzVersion, gasLimit - extra for minting
            )

            nativeFee, _ = await self.estimateSendFee(
                LAYERZERO_CHAINS_ID[self.to_chain],
                self.token_id,
                self.manager.address,
                False,
                adapterParams
            )

            gas = await self.contract.functions.sendFrom(
                self.manager.address,
                LAYERZERO_CHAINS_ID[self.to_chain],
                self.manager.address,
                self.token_id,
                self.manager.address,
                ZERO_ADDRESS,
                adapterParams
            ).estimate_gas(
                {
                    "from": self.manager.address,
                    "value": nativeFee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': 1,
                }
            )
            contract_txn = await self.contract.functions.sendFrom(
                self.manager.address,
                LAYERZERO_CHAINS_ID[self.to_chain],
                self.manager.address,
                self.token_id,
                self.manager.address,
                ZERO_ADDRESS,
                adapterParams
            ).build_transaction(
                {
                    "from": self.manager.address,
                    "value": nativeFee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': gas,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)
            return contract_txn
            
        # except Exception as error:
        #     logger.error(error)
        #     list_send.append(f'{STR_CANCEL}{self.module_str} | {error}')
        #     return False

class Bridger:
    def __init__(self, number, key):
        self.number = number
        self.key = key
        self.from_chain = random.choice(Value_Zerius_ONFT.ValueBridge.from_chain)
        self.to_chain = random.choice(Value_Zerius_ONFT.ValueBridge.to_chain)
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.module_str = f'{self.number} {self.manager.address} | bridge nft {self.from_chain} => {self.to_chain}'

    async def run(self, retry=0):

        if (LAYERZERO_CHAINS_ID[self.from_chain], LAYERZERO_CHAINS_ID[self.to_chain]) in EXCLUDED_LZ_PAIRS or (LAYERZERO_CHAINS_ID[self.to_chain], LAYERZERO_CHAINS_ID[self.from_chain]) in EXCLUDED_LZ_PAIRS:
            logger.error(f'{self.module_str} | this pair of networks is not available for bridge')
            return False

        self.contract = await get_contract(self.from_chain)
        count = await get_balance_nfts_amount(self.contract, self.manager.address)
        tokens_id = [await get_balance_nfts_id(self.contract, self.manager.address, i) for i in range(count)]

        if count == 0:
            logger.error(f'{self.module_str} | nft balance = 0')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return False

        if Value_Zerius_ONFT.ValueBridge.bridge_all:
            counts = count
        else:
            counts = Value_Zerius_ONFT.ValueBridge.amount

        for i in range(counts):
            token_id = tokens_id[i]

            function = Bridge(self.key, self.number, self.from_chain, self.to_chain, token_id, self.manager, self.module_str, self.contract)
            contract_txn = await function.get_txn()
            if not contract_txn:
                logger.error(f'{self.module_str} | error getting contract_txn')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                continue

            status, tx_link = await self.manager.send_tx(contract_txn)

            if status == 1:
                logger.success(f'{self.module_str} | {tx_link}')
                list_send.append(f'{STR_DONE}{self.module_str}')
            else:
                logger.error(f'{self.number} {self.manager.address} | tx is failed | {tx_link}')
                if retry < RETRY:
                    logger.info(f'try again in 10 sec.')
                    await asyncio.sleep(10)
                    return await self.run(retry+1)
                else:
                    list_send.append(f'{STR_CANCEL}{self.module_str}')

            if i+1 != counts:
                await async_sleeping(*DELAY_SLEEP)
            
class Minter:
    def __init__(self, number, key) -> None:
        self.number = number
        self.key = key

    async def main(self, retry=0):
        function = Mint(self.key, self.number, Value_Zerius_ONFT.ValueMint.chain)
        contract_txn = await function.get_txn()
        if not contract_txn:
            logger.error(f'{function.module_str} | error getting contract_txn')
            list_send.append(f'{STR_CANCEL}{function.module_str}')
            return False

        status, tx_link = await function.manager.send_tx(contract_txn)

        if status == 1:
            logger.success(f'{function.module_str} | {tx_link}')
            list_send.append(f'{STR_DONE}{function.module_str}')
        else:
            logger.error(f'{self.number} {function.manager.address} | tx is failed | {tx_link}')
            if retry < RETRY:
                logger.info(f'try again in 10 sec.')
                await asyncio.sleep(10)
                return await self.main(retry+1)
            else:
                list_send.append(f'{STR_CANCEL}{function.module_str}')
            
    async def run(self):
        timer = random.randint(*Value_Zerius_ONFT.ValueMint.amount_mint)
        for i in range(timer):
            await self.main()
            if i+1 != timer:
                await async_sleeping(*DELAY_SLEEP)

class MintBridge:
    def __init__(self, number, key) -> None:
        self.number = number
        self.key = key
        self.from_chain = random.choice(Value_Zerius_ONFT.ValueMintBridge.from_chain)
        self.to_chain = random.choice(Value_Zerius_ONFT.ValueMintBridge.to_chain)
        self.maxPrice = Value_Zerius_ONFT.ValueMintBridge.max_price
        self.amount = random.randint(*Value_Zerius_ONFT.ValueMintBridge.amount)
        self.Web3ManagerAsync = Web3ManagerAsync(key, self.from_chain)
        self.module_str = f'{self.number} {self.Web3ManagerAsync.address} | mint&bridge | {self.from_chain} => {self.to_chain}'

    async def get_nft_balance_in_chain(self, address) -> Decimal:
        return await self.contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
    
    async def get_first_token_id_on_chain(self, address) -> int | None:
        balance = await self.get_nft_balance_in_chain(address)
        if balance == 0:
            return None
        
        tokenId = await self.contract.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(address), 0).call()
        return tokenId
    
    def get_address(self, key):
        try:
            return Account().from_key(key).address
        except:
            return None
        
    def get_token_usd_price(self) -> int:
        tokenToId = {
            'ETH': 'ethereum',
            'MATIC': 'matic-network',
            'BNB': 'binancecoin',
            'AVAX': 'avalanche-2'
        }
        coingeckoRequestUrl = COINGECKO_URL.format(",".join(tokenToId.values()))
        response = requests.get(coingeckoRequestUrl).json()
        prices = {token: response[tokenToId[token]]["usd"] for token in tokenToId.keys()}
        token = LZ_CHAIN_TO_TOKEN[LAYERZERO_CHAINS_ID[self.from_chain]]
        price = prices[token]
        return price
    
    async def estimateMintBridge(self, address) -> Decimal:
        tokenPrice = Decimal(self.get_token_usd_price())
        mintFee = await self.contract.functions.mintFee().call()
        w3 = self.Web3ManagerAsync.get_web3()
        mintFeeEth = Web3.from_wei(mintFee, 'ether')
        mintFeeUsd = mintFeeEth * tokenPrice

        adapterParams = encode_packed(
            ["uint16", "uint256"],
            [1, await self.contract.functions.minDstGasLookup(LAYERZERO_CHAINS_ID[self.to_chain], 1).call()]
        )
        nativeFee, _ = await self.contract.functions.estimateSendFee(
            LAYERZERO_CHAINS_ID[self.to_chain],
            address,
            await self.contract.functions.tokenCounter().call() - 1,
            False,
            adapterParams
        ).call()
        gas = ZERIUS_SEND_GAS_LIMIT[LAYERZERO_CHAINS_ID[self.from_chain]] * await w3.eth.gas_price
        sum = nativeFee + gas
        sumEth = Web3.from_wei(sum, 'ether')
        sumUsd = sumEth * tokenPrice

        return mintFeeUsd + sumUsd

    async def main(self):

        if (LAYERZERO_CHAINS_ID[self.from_chain], LAYERZERO_CHAINS_ID[self.to_chain]) in EXCLUDED_LZ_PAIRS or (LAYERZERO_CHAINS_ID[self.to_chain], LAYERZERO_CHAINS_ID[self.from_chain]) in EXCLUDED_LZ_PAIRS:
            logger.error(f'{self.module_str} | this pair of networks is not available for bridge')
            return False
        
        self.contract = await get_contract(self.from_chain)
        address = self.get_address(self.key)
        if address == None:
            logger.error(f'{self.module_str} | invalid key')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return False
        
        fee = await self.estimateMintBridge(address)
        if (fee > self.maxPrice):
            logger.error(f'{self.module_str} | estimated fee is more than max price: fee= {fee}, max_price= {self.maxPrice}')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return
        
        logger.info(f'{self.module_str} | minting on {self.from_chain}')
        func = Mint(self.key, self.number, [self.from_chain])
        retryMint = 0
        statusMint = 0
        tx_link_mint = ""
        while statusMint != 1 or retryMint < RETRY:
            retryMint += 1
            contract_txn = await func.get_txn()
            if not contract_txn:
                logger.error(f'{self.module_str} | error getting contract_txn for first mint')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                return
        
            statusMint, tx_link_mint = await func.manager.send_tx(contract_txn)
            if statusMint != 1:
                logger.error(f'{self.module_str} | tx is failed | {tx_link_mint}')
                if retryMint < RETRY:
                    logger.info(f'try again in 10 sec.')
            else:
                logger.success(f'{self.module_str} | MINT: {tx_link_mint}')
                list_send.append(f'{STR_CANCEL}{self.module_str} MINT {self.from_chain}')
        if statusMint == 0:
            list_send.append(f'{STR_CANCEL}{self.module_str} MINT {self.from_chain}')
            return False
        await async_sleeping(*DELAY_SLEEP)
        
        balanceOnStart = await self.get_nft_balance_in_chain(address)
        timer = 0
        while balanceOnStart == 0:
            if (timer >= Value_Zerius_ONFT.max_waiting_nft):
                break
            logger.info(f'waiting for nft on {self.from_chain}. try again in 10 sec.')
            timer += 10
            await asyncio.sleep(10)
            balanceOnStart = await self.get_nft_balance_in_chain(address)
        if balanceOnStart == 0:
            logger.error(f'{self.module_str} | error timeout waiting nft on {self.from_chain}')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return False
        logger.success(f'{self.module_str} | balance on {self.from_chain}: {balanceOnStart}')
        await async_sleeping(*DELAY_SLEEP)

        tokenId = await self.get_first_token_id_on_chain(address)
        logger.info(f'{self.module_str} | start bridge token {tokenId} | {self.from_chain} => {self.to_chain}')

        function = Bridge(self.key, self.number, self.from_chain, self.to_chain, tokenId, self.Web3ManagerAsync, self.module_str, self.contract)

        retryBridge = 0
        status = 0
        tx_link = ""
        while status != 1 or retryBridge < RETRY:
            retryBridge += 1
            contract_txn = await function.get_txn()
            if not contract_txn:
                logger.error(f'{self.module_str} | error getting contract_txn for bridge {self.from_chain} -> {self.to_chain}')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                return
        
            status, tx_link = await function.manager.send_tx(contract_txn)
            if status != 1:
                logger.error(f'{self.module_str} | tx is failed | {tx_link}')
                if retryBridge < RETRY:
                    logger.info(f'try again in 10 sec.')
            else:
                logger.success(f'{self.module_str} | BRIDGE {self.from_chain} -> {self.to_chain}: {tx_link}')
                list_send.append(f'{STR_CANCEL}{self.module_str} BRIDGE {self.from_chain} -> {self.to_chain}')
        if status == 0:
            return False
        return True
    
    async def run(self):
        for i in range(self.amount):
            await self.main()
            if i+1 != self.amount:
                await async_sleeping(*DELAY_SLEEP)

class Ultra:
    # Request limit 
    LIMIT = asyncio.Semaphore(5)

    def __init__(self, number, key) -> None:
        self.number = number
        self.key = key
        self.maxBridgePrice = Value_Zerius_ONFT.ValueUltra.max_bridge_price
        self.bridgesCount = random.randint(*Value_Zerius_ONFT.ValueUltra.bridges_count)
        fromChain = Value_Zerius_ONFT.ValueUltra.from_chain
        if not fromChain:
            self.fromChain = None
        else:
            self.fromChain = random.choice(fromChain)
        self.chains = Value_Zerius_ONFT.ValueUltra.included_chains
        if self.fromChain != None and self.fromChain not in self.chains:
            self.chains.append(self.fromChain)
        self.manager = Web3ManagerAsync(self.key, "ethereum")
        self.module_str = f'{self.number} {self.manager.address} | ultra'
        self.bridgeMatrix = None

    def get_address(self, key):
        try:
            return Account().from_key(key).address
        except:
            return None
        
    async def get_balance_in_chains(self, address, Web3ManagerAsyncs, tokenPrices) -> dict[int, Decimal]:
        balancesUsd = {}
        for chain in self.chains:
            lzChainId = LAYERZERO_CHAINS_ID[chain]
            w3 = Web3ManagerAsyncs[lzChainId].get_web3()
            balance = await w3.eth.get_balance(Web3.to_checksum_address(address))
            balanceEth = Web3.from_wei(balance, 'ether')
            tokenPrice = Decimal(tokenPrices[lzChainId])
            balanceUsd = balanceEth * tokenPrice
            balancesUsd[chain] = balanceUsd
        return balancesUsd
        
    def get_tokens_usd_prices(self) -> dict[str, Decimal]:
        tokenToId = {
            'ETH': 'ethereum',
            'MATIC': 'matic-network',
            'BNB': 'binancecoin',
            'AVAX': 'avalanche-2'
        }
        coingeckoRequestUrl = COINGECKO_URL.format(",".join(tokenToId.values()))
        response = requests.get(coingeckoRequestUrl).json()
        prices = {token: response[tokenToId[token]]["usd"] for token in tokenToId.keys()}
        to_chainPrice = {LAYERZERO_CHAINS_ID[chain]: prices[LZ_CHAIN_TO_TOKEN[LAYERZERO_CHAINS_ID[chain]]] for chain in self.chains}
        return to_chainPrice
    
    async def estimate_bridge(
            self, 
            address, 
            srcZerius,
            srcLzId,
            dstLzId,
            tokenPrice,
            Web3ManagerAsync: Web3ManagerAsync,
            token
        ) -> (int, int, Decimal):
        async with self.LIMIT:
            return await self._estimate_bridge(
            address, 
            srcZerius,
            srcLzId,
            dstLzId,
            tokenPrice,
            Web3ManagerAsync,
            token
        )

    async def _estimate_bridge(
            self, 
            address, 
            srcZerius,
            srcLzId,
            dstLzId,
            tokenPrice,
            Web3ManagerAsync: Web3ManagerAsync,
            token
        ) -> (int, int, Decimal):
        adapterParams = encode_packed(
            ["uint16", "uint256"],
            [1, await srcZerius.functions.minDstGasLookup(dstLzId, 1).call()]
        )
        fromAddress = Web3.to_checksum_address(address)
        success = False
        retry = 0
        nativeFee = None
        while not success or retry < RETRY:
            try:
                retry += 1
                nativeFee, _ = await srcZerius.functions.estimateSendBatchFee(
                    dstLzId,
                    fromAddress,
                    [token],
                    False,
                    adapterParams
                ).call()
                success = True
            except Exception as error:
                logger.error(f'{self.module_str} | error estimating native fee for bridge {srcLzId} -> {dstLzId}: {error}')
                if (retry < RETRY):
                    logger.info(f'try again in 10 sec.')
                    await asyncio.sleep(10)
                else:
                    logger.error(f'{self.module_str} | FAILED estimating native fee for bridge {srcLzId} -> {dstLzId}')
                    return
        w3 = Web3ManagerAsync.get_web3()
        gas = ZERIUS_SEND_GAS_LIMIT[srcLzId] * await w3.eth.gas_price
        sumWei = gas + nativeFee
        sumEth = w3.from_wei(sumWei, 'ether')
        sumUsd = Decimal(tokenPrice) * sumEth
        return (srcLzId, dstLzId, sumUsd)
    
    async def create_bridge_matrix(self, address, contracts: dict, tokenPrices, Web3ManagerAsyncs):
        matrix = {}
        for (srcLzId, srcZerius) in contracts.items():
            dst = []
            for (dstLzId, _) in contracts.items():
                if srcLzId == dstLzId or (srcLzId, dstLzId) in EXCLUDED_LZ_PAIRS or (dstLzId, srcLzId) in EXCLUDED_LZ_PAIRS: continue
                dst.append(dstLzId)
            token = await srcZerius.functions.tokenCounter().call() - 1
            coroutines = [self.estimate_bridge(address, srcZerius, srcLzId, dstLzId, tokenPrices[srcLzId], Web3ManagerAsyncs[srcLzId], token) for dstLzId in dst]
            res = await asyncio.gather(*coroutines)
            matrix[srcLzId] = {}
            for (_, dstLzId, cost) in res:
                matrix[srcLzId][dstLzId] = cost
        return matrix
    
    async def get_lowcost_bridges(self, address, contracts: dict, tokenPrices, Web3ManagerAsyncs):
        if self.bridgeMatrix == None:
            self.bridgeMatrix = await self.create_bridge_matrix(address, contracts, tokenPrices, Web3ManagerAsyncs)
        lowcostBridges = {}
        for srcLzChain in self.bridgeMatrix.keys():
            dstLzChainsSorted = sorted(self.bridgeMatrix[srcLzChain].items(), key=lambda item: item[1])
            dstLzChainsFiltered = [item for item in filter(lambda item: item[1] < self.maxBridgePrice, dstLzChainsSorted)]
            if (len(dstLzChainsFiltered) > 0):
                lowcostBridges[srcLzChain] = dstLzChainsFiltered[:3]

        return lowcostBridges
    
    async def get_mint_prices(
            self,
            fromAddress,
            tokenPrices,
            contracts,
            Web3ManagerAsyncs,
            availableChains
    ) -> dict[int, Decimal]:
        mintPrices = {}
        for lzChain in availableChains:
            contract = contracts[lzChain]
            nftsBalance = await self.get_nft_balance_in_chain(fromAddress, contract)
            if nftsBalance == 0:
                mintFeeNative = await contract.functions.mintFee().call()
                mintGas = Decimal(ZERIUS_MINT_GAS_LIMIT[lzChain]) * await Web3ManagerAsyncs[lzChain].get_web3().eth.gas_price
                mintPriceEth = Web3.from_wei(mintFeeNative + mintGas, 'ether')
                mintPriceUsd = mintPriceEth * Decimal(tokenPrices[lzChain])
                mintPrices[lzChain] = mintPriceUsd
            else:
                mintPrices[lzChain] = Decimal(0)

        return mintPrices
    
    async def get_nft_balance_in_chain(self, address, contract) -> Decimal:
        return await contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
    
    def get_chain_name_for_lz_id(self, lzId):
        return list(LAYERZERO_CHAINS_ID.keys())[list(LAYERZERO_CHAINS_ID.values()).index(lzId)]
    
    async def get_first_token_id_on_chain(self, address, contract) -> int | None:
        balance = await self.get_nft_balance_in_chain(address, contract)
        if balance == 0:
            return None
        
        tokenId = await contract.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(address), 0).call()
        return tokenId
    
    async def mint(self, chain) -> bool:
        logger.info(f'{self.module_str} | minting on {chain}')
        func = Mint(self.key, self.number, [chain])
        retryMint = 0
        status = 0
        tx_link = ""
        while status != 1 or retryMint < RETRY:
            retryMint += 1
            contract_txn = await func.get_txn()
            if not contract_txn:
                logger.error(f'{self.module_str} | error getting contract_txn for first mint')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                return
        
            status, tx_link = await func.manager.send_tx(contract_txn)
            if status != 1:
                logger.error(f'{self.module_str} | tx is failed | {tx_link}')
                if retryMint < RETRY:
                    logger.info(f'try again in 10 sec.')
            else:
                logger.success(f'{self.module_str} | MINT: {tx_link}')
                list_send.append(f'{STR_DONE}{self.module_str} MINT {chain}')
        if status == 0:
            logger.error(f'{self.module_str} | MINT FAIL: {tx_link}')
            list_send.append(f'{STR_CANCEL}{self.module_str} MINT {chain}')
            return False
        return True
    
    async def bridge(
            self, 
            bridgesCount,
            address, 
            lowcostBridgesMatrix,
            Web3ManagerAsyncs, 
            contracts, 
            srcLzChain,
            dstLzChain = None, 
            dstChainName = None
        ):
        srcChainName = self.get_chain_name_for_lz_id(srcLzChain)
        logger.info(f'{self.module_str} | {bridgesCount} bridge: bridging from {srcChainName}')

        balanceOnStart = await self.get_nft_balance_in_chain(address, contracts[srcLzChain])
        timer = 0
        while balanceOnStart == 0:
            if (timer >= Value_Zerius_ONFT.max_waiting_nft):
                break
            logger.info(f'waiting for nft on {srcChainName}. Try again in 10 sec.')
            timer += 10
            await asyncio.sleep(10)
            balanceOnStart = await self.get_nft_balance_in_chain(address, contracts[srcLzChain])
        if balanceOnStart == 0:
            logger.error(f'{self.module_str} | error timeout waiting nft on {srcChainName}')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return False, None
        logger.success(f'{self.module_str} | balance on {srcChainName}: {balanceOnStart}')
        await async_sleeping(*DELAY_SLEEP)

        if dstLzChain == None:
            logger.info(f'{self.module_str} | {bridgesCount} bridge: searching for cheapest dst')
            randomCeiling = min(2, len(lowcostBridgesMatrix[srcLzChain]) - 1)
            randomDst = random.randint(0, randomCeiling)
            dstLzChain = lowcostBridgesMatrix[srcLzChain][randomDst][0]
            dstChainName = self.get_chain_name_for_lz_id(dstLzChain)
            # logger.success(f'{self.module_str} | {bridgesCount} bridge: found cheapest dst - {dstChainName}')
            
        tokenId = await self.get_first_token_id_on_chain(address, contracts[srcLzChain])
        logger.info(f'{self.module_str} | start bridge token {tokenId} | {srcChainName} => {dstChainName}')

        function = Bridge(self.key, self.number, srcChainName, dstChainName, tokenId, Web3ManagerAsyncs[srcLzChain], self.module_str, contracts[srcLzChain])

        retryBridge = 0
        status = 0
        tx_link = ""
        while status != 1 or retryBridge < RETRY:
            retryBridge += 1
            contract_txn = await function.get_txn()
            if not contract_txn:
                logger.error(f'{self.module_str} | error getting contract_txn for bridge {srcChainName} -> {dstChainName}')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                return
        
            status, tx_link = await function.manager.send_tx(contract_txn)
            if status != 1:
                logger.error(f'{self.module_str} | tx is failed | {tx_link}')
                if retryBridge < RETRY:
                    logger.info(f'try again in 10 sec.')
            else:
                logger.success(f'{self.module_str} | BRIDGE {srcChainName} -> {dstChainName}: {tx_link}')
                list_send.append(f'{STR_DONE}{self.module_str} BRIDGE {srcChainName} -> {dstChainName}')
        if status == 0:
            logger.error(f'{self.module_str} | FAIL BRIDGE {srcChainName} -> {dstChainName}')
            list_send.append(f'{STR_CANCEL}{self.module_str} BRIDGE {srcChainName} -> {dstChainName}')
            return False, None
        return True, dstLzChain
    
    async def main(self):
        logger.info(f'{self.module_str} | START CHAIN BRIDGE')
        fromAddress = self.get_address(self.key)
        if fromAddress == None:
            logger.error(f'{self.module_str} | invalid key')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return
        
        Web3ManagerAsyncs = {LAYERZERO_CHAINS_ID[chain]: Web3ManagerAsync(self.key, chain) for chain in self.chains}

        # logger.info(f'{self.module_str} | get tokens prices from coingecko')
        tokensPricesUsd = self.get_tokens_usd_prices()

        # logger.info(f'{self.module_str} | get native balances for address')
        balancesUsd = await self.get_balance_in_chains(fromAddress, Web3ManagerAsyncs, tokensPricesUsd)

        # logger.info(f'{self.module_str} | checking chains availability')
        availableChains = []
        for chain in balancesUsd.keys():
            if balancesUsd[chain] > Decimal(1):
                availableChains.append(chain)
        if len(availableChains) == 0:
            logger.error(f'{self.module_str} | can\'t find available chains, try to top up your balances')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return
        logger.success(f'{self.module_str} | found {len(availableChains)} chains with sufficient balance: {", ".join(availableChains)}')
        contracts = {LAYERZERO_CHAINS_ID[chain]: await get_contract(chain) for chain in availableChains}

        # logger.info(f'{self.module_str} | building lowcost bridges matrix\nIt might take some time. Please wait...')
        lowcostBridgesMatrix = await self.get_lowcost_bridges(fromAddress, contracts, tokensPricesUsd, Web3ManagerAsyncs)
        if len(lowcostBridgesMatrix) == 0:
            logger.error(f'{self.module_str} | can\'t find ultra options, try to change max bridge price')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return
        
        if (self.fromChain == None):
            availableLzChainsForBridge = list(lowcostBridgesMatrix.keys())
            # logger.success(f'{self.module_str} | found {len(availableLzChainsForBridge)} available LZ chains: {", ".join([str(i) for i in availableLzChainsForBridge])}')
    
            # logger.info(f'{self.module_str} | estimating mint fees')
            firstMint = await self.get_mint_prices(fromAddress, tokensPricesUsd, contracts, Web3ManagerAsyncs, availableLzChainsForBridge)
    
            # logger.info(f'{self.module_str} | searching for the cheapest chain to start bridging')
            mintBridge = {chain: firstMint[chain] + lowcostBridgesMatrix[chain][0][1] for chain in availableLzChainsForBridge}
            mintBridgeSorted = sorted(mintBridge.items(), key=lambda item: item[1])
    
            randomCeiling = min(2, len(mintBridgeSorted) - 1)
            randomStart = random.randint(0, randomCeiling)
    
            srcLzChain = mintBridgeSorted[randomStart][0]
            srcChainName = self.get_chain_name_for_lz_id(srcLzChain)
            logger.info(f'{self.module_str} | found the cheapest LZ chain to start bridging - {srcChainName}')
        else:
            srcLzChain = LAYERZERO_CHAINS_ID[self.fromChain]
            srcChainName = self.fromChain
            if srcChainName not in availableChains:
                logger.error(f'{self.module_str} | chain {srcChainName} is unavailabe: insufficient balance or max bridge price is too low')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                return
        if srcChainName not in availableChains:
            logger.error(f'{self.module_str} | invalid src chains, invalid balances')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return
        if srcLzChain not in lowcostBridgesMatrix.keys():
            logger.error(f'{self.module_str} | invalid src chains, max bridge price is too low or insufficient balances')
            list_send.append(f'{STR_CANCEL}{self.module_str}')
            return
        
        needMint = await self.get_nft_balance_in_chain(fromAddress, contracts[srcLzChain]) == 0
        if (needMint):
            success = await self.mint(srcChainName)
            if not success:
                return
            await async_sleeping(*DELAY_SLEEP)
        dstLzChain = lowcostBridgesMatrix[srcLzChain][0][0]
        dstChainName = self.get_chain_name_for_lz_id(dstLzChain)
            
        bridgesCount = 1
        while bridgesCount <= self.bridgesCount:
            # logger.info(f'{self.module_str} | checking native balances')
            balancesUsd = await self.get_balance_in_chains(fromAddress, Web3ManagerAsyncs, tokensPricesUsd)
            availableChains = []
            for chain in balancesUsd.keys():
                if balancesUsd[chain] > Decimal(1):
                    availableChains.append(chain)
            if len(lowcostBridgesMatrix.keys()) < 2 and srcLzChain not in availableChains:
                logger.error(f'{self.module_str} | less than 2 chains are available, max bridge price is too low or insufficient balances')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                return
            
            contracts = {LAYERZERO_CHAINS_ID[chain]: await get_contract(chain) for chain in availableChains}
            
            # logger.info(f'{self.module_str} | building lowcost bridges matrix')
            lowcostBridgesMatrix = await self.get_lowcost_bridges(fromAddress, contracts, tokensPricesUsd, Web3ManagerAsyncs)
            if len(lowcostBridgesMatrix.keys()) < 2 and srcLzChain not in lowcostBridgesMatrix.keys():
                logger.error(f'{self.module_str} | less than 2 chains are available, max bridge price is too low or insufficient balances')
                list_send.append(f'{STR_CANCEL}{self.module_str}')
                return
            
            (success, newSrcLzChain) = await self.bridge(bridgesCount, fromAddress, lowcostBridgesMatrix, Web3ManagerAsyncs, contracts, srcLzChain, dstLzChain, dstChainName)
            if not success:
                return
            dstLzChain = None
            dstChainName = None
            srcLzChain = newSrcLzChain
            bridgesCount += 1
            await async_sleeping(*DELAY_SLEEP)

    async def run(self):
        # logger.info(f'{self.module_str} | Start chain bridge with length {self.bridgesCount}')
        if ('polygon' in self.chains):
            logger.warning(f'{self.module_str} | Bridging to/from Polygon may take a lot of time. Remove Polygon from included chains in case of unpredictable script behaviour')
        await self.main()
        
class CheckNFTs:
    def __init__(self, wallets):
        self.wallets = [self.get_address(wallet) for wallet in wallets]
        self.file_name = "result/balances.csv"

    def get_address(self, key):
        try:
            return Account().from_key(key).address
        except:
            return key
        
    def send_result(self, result_balances, total_balances):
        headers = [['number', 'wallet', 'total'], [], ['TOTAL_AMOUNTS', '', sum([value for value in total_balances.values()])]]
        send_table = []
        for number, (wallet, chains) in enumerate(result_balances.items(), start=1):
            h_ = [number, wallet, total_balances[wallet]]

            for chain, balance in chains.items():
                if chain not in headers[0]:
                    headers[0].append(chain)
                h_.append(balance)
            headers[1].append(h_)
            send_table.append(h_)

        with open(self.file_name, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(headers[0])
            spamwriter.writerows(headers[1])

        table_type = 'double_grid'
        tokens = tabulate(send_table, headers[0], tablefmt=table_type)

        cprint(f'\nAll balances :\n', 'blue')
        cprint(tokens, 'white')
        cprint(f'Total balances : {sum([value for value in total_balances.values()])}', 'blue')
        cprint(f'\nResults written to file: {self.file_name}\n', 'blue')

    async def main(self):
        tasks = []
        for wallet in self.wallets:
            for chain in ZERIUS_CONTRACTS:
                contract = await get_contract(chain)
                tasks.append(get_balance_nfts_amount(contract, wallet))


        _res = await asyncio.gather(*tasks)
        _result = [_res[i:i + len(ZERIUS_CONTRACTS)] for i in range(0, len(_res), (len(ZERIUS_CONTRACTS)))]

        result_balances = {}
        for number, wallet in enumerate(self.wallets):
            wallet = wallet.lower()
            result_balances[wallet] = {}
            balances = _result[number]
            for i, chain in enumerate(ZERIUS_CONTRACTS):
                balance = balances[i]
                result_balances[wallet][chain] = balance

        total_balances = {wallet: sum(amount.values()) for wallet, amount in result_balances.items()}

        self.send_result(result_balances, total_balances)

MODULES = {
    1: ("ultra", Ultra),
    2: ("mint_bridge", MintBridge),
    3: ("mint", Minter),
    4: ("bridge", Bridger),
    5: ("check_nfts", CheckNFTs),
}

def get_module(module):
    module_info = MODULES.get(module)
    if module_info:
        module_name, func = module_info
        # cprint(f'\nstart : {module_name}', 'white')
        return func, module_name
    else:
        raise ValueError(f"Unsupported module: {module}")

async def worker(func, key, number):
    function = func(number, key)
    await function.run()

async def process_batches(func, wallets):
    batches = [wallets[i:i + WALLETS_IN_BATCH] for i in range(0, len(wallets), WALLETS_IN_BATCH)]

    number = 0
    for batch in batches:
        res = []
        try:
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

        except Exception as error:
            logger.error(error)

        if (TG_BOT_SEND and len(list_send) > 0):
            send_msg()
            
        if IS_SLEEP:
            await async_sleeping(*DELAY_SLEEP)

        list_send.clear()

async def Zerius():
    module = int(input('''
ZERIUS MODULE:
1.  ultra
2.  mint + bridge
3.  mint
4.  bridge
5.  check nfts

Choose a module (1 - 5) : '''))
    
    func, module_name = get_module(module)

    if module == 5:
        await func(WALLETS).main()
    else:
        if RANDOMIZER:
            random.shuffle(WALLETS)
        await process_batches(func, WALLETS)
