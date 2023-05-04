
from config import *

get_result = {
    'token' : {},
    'nft' : {
        'op'    : {},
        'eth'   : {},
        'arb'   : {},
        'matic' : {},
        'bsc'   : {},
    },
    'protocol' : {}
}

def evm_wallet(key):

    try:
        web3 = Web3(Web3.HTTPProvider(DATA['ethereum']['rpc']))
        wallet = web3.eth.account.from_key(key).address
        return wallet
    except:
        return key

async def get_debank(session, address, type_, chain=''):

    while True:

        try:

            sleep = 3

            urls = {
                'token'     : f'https://api.debank.com/token/cache_balance_list?user_addr={address}',
                'nft'       : f'https://api.debank.com/nft/collection_list?user_addr={address}&chain={chain}',
                'protocol'  : f'https://api.debank.com/portfolio/project_list?user_addr={address}',
            }

            proxy = random.choice(PROXIES)

            async with session.get(urls[type_], proxy=proxy, timeout=10) as resp:

                if resp.status == 200:
                    resp_json = await resp.json(content_type=None)
                    if type_ == 'nft': 
   
                        if resp_json['data']['job']: 
                            await asyncio.sleep(sleep)
                        else:

                            get_result[type_][chain].update({address : resp_json})
                            logger.success(f'{address} | {type_} : {chain}')
                            break

                    else:
                        get_result[type_].update({address : resp_json})
                        logger.success(f'{address} | {type_}')
                        break
                else:
                    # logger.info(f'resp.status = {resp.status}, try again in {sleep} sec.')
                    await asyncio.sleep(sleep)

        except Exception as error:
            logger.info(f'{address} | {type_} : {error}')
            await asyncio.sleep(3)

async def checker_main(modules, nft_chains, wallets):

    async with aiohttp.ClientSession() as session:
        tasks = []

        for address in wallets:


            if 'token' in modules:

                task = asyncio.create_task(get_debank(session, address, 'token'))
                tasks.append(task)


            if 'protocol' in modules:

                task = asyncio.create_task(get_debank(session, address, 'protocol'))
                tasks.append(task)
                

            if 'nft' in modules:

                for chain in nft_chains:

                    task = asyncio.create_task(get_debank(session, address, 'nft', chain))
                    tasks.append(task)


        await asyncio.gather(*tasks)

def get_json_data(check_min_value, wallets):

    total_result = {}

    for wallet in wallets:
        total_result.update({wallet : {
            'token' : [],
            'nft' : [],
            'protocol' : [],
            'protocol_value' : 0,
            'token_value' : 0,
            'total_value' : 0,
        }})


    # check tokens
    for tokens in get_result['token'].items():
        
        wallet  = tokens[0]
        data    = tokens[1]

        for items in data['data']:

            chain   = items['chain'].upper()
            price   = items['price']
            amount  = items['amount']
            symbol  = items['optimized_symbol']
            value   = amount * price
            
            if value > check_min_value:

                total_result[wallet]['token'].append(
                    {
                        'chain'     : chain,
                        'symbol'    : symbol,
                        'amount'    : amount,
                        'value'     : value,
                    }
                )

                total_result[wallet]['token_value'] += value

    # check nfts
    for nfts in get_result['nft'].items():

        chain = nfts[0].upper()
        data_ = nfts[1]
        
        for w_ in data_.items():

            wallet  = w_[0]
            data    = w_[1]

            for items in data['data']['result']['data']:

                amount  = items['amount']
                name    = items['name']

                total_result[wallet]['nft'].append(
                    {
                        'chain'     : chain,
                        'name'      : name,
                        'amount'    : amount,
                    }
                )

    # check protocols
    for tokens in get_result['protocol'].items():
        
        wallet  = tokens[0]
        data    = tokens[1]

        for items in data['data']:

            chain   = items['chain'].upper()
            name    = items['name']
            value   = int(items['portfolio_item_list'][0]['stats']['asset_usd_value'])
            
            if value > check_min_value:

                total_result[wallet]['protocol'].append(
                    {
                        'chain'     : chain,
                        'name'      : name,
                        'value'     : value,
                    }
                )

                total_result[wallet]['protocol_value'] += value

    # check total value
    for wallet in wallets:
        total_result[wallet]['total_value'] = total_result[wallet]['protocol_value'] + total_result[wallet]['token_value']

    # call_json(total_result, 'test2')

    return total_result

def round_to(num, digits=3):
    try:
        if num == 0: return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits: scale = digits
        return round(num, scale)
    except: return num

def send_result(get_json, file_name, check_chain, check_coin):


    file = open(f'{outfile}results/{file_name}.txt', 'w', encoding='utf-8')

    with open(f'{outfile}results/{file_name}.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        spamwriter.writerow(['number', 'wallet', 'balance $', 'protocols $', 'tokens $', 'nft amount'])

        all_wallets_value = []
        all_finder_token = []

        zero = 0
        for wallets in get_json.items():
            zero+= 1

            wallet = wallets[0]
            data = wallets[1]

            file.write(f'\n{zero}. {wallet}\n')

            tokens = []
            for items in data['token']:

                chain   = items['chain']
                symbol  = items['symbol']
                amount  = round_to(items['amount'])
                value   = int(items['value'])

                tokens.append([chain, amount, symbol, f'{value} $'])

                if check_chain != '':
                    if check_chain == chain:
                        if check_coin == symbol:
                            finder = amount
                else:
                        if check_coin == symbol:
                            finder = amount

            protocols = []
            for items in data['protocol']:

                chain   = items['chain']
                name    = items['name']
                value   = int(items['value'])

                protocols.append([chain, name, f'{value} $'])

            nfts = []
            nft_amounts = []
            for items in data['nft']:

                chain   = items['chain']
                name    = items['name']
                amount  = int(items['amount'])

                nft_amounts.append(amount)
                nfts.append([chain, name, amount])

            protocol_value  = int(data['protocol_value'])
            token_value     = int(data['token_value'])
            total_value     = int(data['total_value'])

            table_type  = 'double_outline'

            head_table  = ['chain', 'amount', 'symbol', 'value']
            tokens_     = tabulate(tokens, head_table, tablefmt=table_type)

            head_table  = ['chain', 'name', 'value']
            protocols_  = tabulate(protocols, head_table, tablefmt=table_type)

            head_table  = ['chain', 'name', 'amount']
            nfts_       = tabulate(nfts, head_table, tablefmt=table_type)


            cprint(f'\n{zero}. {wallet}\n', 'yellow')

            if len(tokens) > 0:
                file.write(f'\n{tokens_}\n')
                cprint(tokens_, 'white')

            if len(protocols) > 0:
                file.write(f'\n{protocols_}\n')
                cprint(protocols_, 'white')

            if len(nfts) > 0:
                file.write(f'\n{nfts_}\n')
                cprint(nfts_, 'white')

            file.write(f'\ntotal_value : {total_value} $\n')
            cprint(f'\ntotal_value : {total_value} $\n', 'green')
            

            if check_coin != '':
                file.write(f'{check_coin} : {finder}\n')
                cprint(f'{check_coin} : {finder}\n', 'green')
                all_finder_token.append(finder)
                

            spamwriter.writerow([zero, wallet, total_value, protocol_value, token_value, sum(nft_amounts)])

            all_wallets_value.append(total_value)

        cprint(f'\n>>> ALL WALLETS VALUE : {sum(all_wallets_value)} $ <<<\n', 'blue')
        file.write(f'\n>>> ALL WALLETS VALUE : {sum(all_wallets_value)} $ <<<\n')
        spamwriter.writerow(['ALL_VALUE :', sum(all_wallets_value)])

        amount_finder_coin = round_to(sum(all_finder_token))
        if amount_finder_coin > 0:
            cprint(f'\n>>> {check_coin} : {amount_finder_coin} $ <<<\n', 'blue')
            file.write(f'\n>>> {check_coin} : {amount_finder_coin} $ <<<\n')
            spamwriter.writerow([f'{check_coin}', amount_finder_coin])

    file.close()

    cprint(f'результаты записаны в файлы : {outfile}{file_name}.csv и {outfile}{file_name}.txt\n', 'blue')


def start_debank():

    wallets = []
    for key in WALLETS:
        wallet = evm_wallet(key)
        wallets.append(wallet)

    file_name, check_min_value, check_chain, check_coin, modules, nft_chains = value_debank()

    asyncio.run(checker_main(modules, nft_chains, wallets))
    get_json = get_json_data(check_min_value, wallets)
    send_result(get_json, file_name, check_chain, check_coin)



