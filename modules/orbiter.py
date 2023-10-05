from .utils.contracts.abi import ABI_ORBITER_TO_STARKNET
from config import ORBITER_MAKER, STR_CANCEL, STARKNET_WALLETS
from .utils.contracts.contract import ORBITER_AMOUNT, ORBITER_AMOUNT_STR, CONTRACTS_ORBITER_TO_STARKNET
from setting import Value_Orbiter
from .utils.helpers import list_send, intToDecimal, round_to
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3
import random, decimal

class OrbiterBridge:
    
    def __init__(self, key, number, params=None):
        self.params = params
        if self.params:
            self.from_chain = self.params['from_chain']
            self.to_chain = self.params['to_chain']
            self.amount_from = self.params['amount_from']
            self.amount_to = self.params['amount_to']
            self.bridge_all_balance = self.params['bridge_all_balance']
            self.min_amount_bridge = self.params['min_amount_bridge']
            self.keep_value_from = self.params['keep_value_from']
            self.keep_value_to = self.params['keep_value_to']
        else:
            self.from_chain = Value_Orbiter.from_chain
            self.to_chain = Value_Orbiter.to_chain
            self.amount_from = Value_Orbiter.amount_from
            self.amount_to = Value_Orbiter.amount_to
            self.bridge_all_balance = Value_Orbiter.bridge_all_balance
            self.min_amount_bridge = Value_Orbiter.min_amount_bridge
            self.keep_value_from = Value_Orbiter.keep_value_from
            self.keep_value_to = Value_Orbiter.keep_value_to
        self.key = key
        self.number = number

    async def setup(self):
        self.from_chain = random.choice(self.from_chain)
        self.to_chain = random.choice(self.to_chain)
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.from_token_data = await self.manager.get_token_info('')
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.bridge_all_balance, '', self.amount_from, self.amount_to)
        self.value = intToDecimal(self.get_orbiter_value(), 18) 
        self.module_str = f'{self.number} {self.manager.address} | orbiter_bridge : {round_to(self.amount)} {self.from_token_data["symbol"]} | {self.from_chain} => {self.to_chain}'

    def get_orbiter_value(self):
        base_num_dec = decimal.Decimal(str(self.amount))
        orbiter_amount_dec = decimal.Decimal(str(ORBITER_AMOUNT[self.to_chain]))
        difference = base_num_dec - orbiter_amount_dec
        random_offset = decimal.Decimal(str(random.uniform(-0.000000000000001, 0.000000000000001)))
        result_dec = difference + random_offset
        orbiter_str = ORBITER_AMOUNT_STR[self.to_chain][-4:]
        result_str = '{:.18f}'.format(result_dec.quantize(decimal.Decimal('0.000000000000000001')))
        result_str = result_str[:-4] + orbiter_str
        return decimal.Decimal(result_str)

    def get_orbiter_limits(self):

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

        from_maker  = orbiter_ids[self.from_chain]
        to_maker    = orbiter_ids[self.to_chain]

        maker_x_maker = f'{from_maker}-{to_maker}'

        for maker in ORBITER_MAKER:

            if maker_x_maker == maker:
                
                min_bridge  = ORBITER_MAKER[maker]['ETH-ETH']['minPrice']
                max_bridge  = ORBITER_MAKER[maker]['ETH-ETH']['maxPrice']
                fees        = ORBITER_MAKER[maker]['ETH-ETH']['tradingFee']

                return min_bridge, max_bridge, fees

    def limit_test(self, min_bridge, max_bridge):
        if (self.amount > min_bridge and self.amount < max_bridge): 
            return True
        else:

            if self.amount < min_bridge:
                logger.error(f"{self.module_str} | {self.amount} (amount) < {min_bridge} (min_bridge)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | {self.amount} less {min_bridge}')

            elif self.amount > max_bridge:
                logger.error(f"{self.module_str} | {self.amount} (amount) > {max_bridge} (max_bridge)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | {self.amount} over {max_bridge}')
            return False

    async def get_txn(self):

        try:

            min_bridge, max_bridge, fees = self.get_orbiter_limits()
            min_bridge = min_bridge + fees

            if self.limit_test(min_bridge, max_bridge) is False: return False

            if self.to_chain == 'starknet':

                starknet_address = STARKNET_WALLETS[self.key]
                if starknet_address[:3] == '0x0': starknet_wallet = f'030{starknet_address[3:]}'
                else                            : starknet_wallet = f'030{starknet_address[2:]}'

                starknet_wallet = bytes.fromhex(starknet_wallet) 

                contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(CONTRACTS_ORBITER_TO_STARKNET[self.from_chain]), abi=ABI_ORBITER_TO_STARKNET)
                contract_txn = await contract.functions.transfer(
                        '0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8', # _to
                        starknet_wallet
                    ).build_transaction(
                    {
                        'chainId': self.manager.chain_id,
                        "from": self.manager.address,
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                        "value": self.value,
                        'gas': 0,
                        'gasPrice': 0
                    }
                )

            else:

                contract_txn = {
                    'chainId': self.manager.chain_id,
                    'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    "from": self.manager.address,
                    'to': '0x80C67432656d59144cEFf962E8fAF8926599bCF8',
                    'value': self.value,
                    'gas': 0,
                    'gasPrice': 0
                }

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit(contract_txn)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.amount >= self.min_amount_bridge:
                return contract_txn
            else:
                logger.error(f"{self.module_str} | {self.amount} (amount) < {self.min_amount_bridge} (min_amount_bridge)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | {self.amount} less {self.min_amount_bridge}')
                return False
            
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} : {error}')
            return False
