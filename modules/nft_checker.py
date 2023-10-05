from config import WALLETS
from setting import Value_NFT_Checker
from .utils.multicall import Multicall
from termcolor import cprint
import csv
from tabulate import tabulate

class NFTChecker:

    def __init__(self):
        self.send_file = f'results/nft_balances.csv'
    
    def write_results_to_csv(self, spamwriter):

        total_amount = []
        for number, (wallet, balance) in enumerate(self.result.items(), start=1):
            spamwriter.writerow([number, wallet, balance])
            total_amount.append(balance)
        
        spamwriter.writerow([])
        spamwriter.writerow(['TOTAL AMOUNT', sum(total_amount)])
    
        return total_amount
    
    def write_small_wallets_to_csv(self, spamwriter, small_wallets):
        for number, wallet in enumerate(small_wallets, start=1):
            cprint(wallet, 'white')
            spamwriter.writerow([number, wallet])

    def print_results(self, total_amount, table):
        cprint(table, 'white')
        cprint(f'\nTOTAL AMOUNT : {sum(total_amount)}', 'white')
        cprint(f'\nРезультаты записаны в файл : {self.send_file}\n', 'blue')

    async def start(self):
        self.result = await Multicall(Value_NFT_Checker.chain).get_nft_balances(WALLETS, Value_NFT_Checker.contract)
        
        with open(self.send_file, 'w', newline='') as csvfile:
            table_head = ['number', 'wallet', 'amount']
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(table_head)
            total_amount = self.write_results_to_csv(spamwriter)

            small_wallets = [wallet for wallet in WALLETS if self.result.get(wallet, 0) < Value_NFT_Checker.min_balance]
            if small_wallets:
                text = f'NFT balance on these wallets < {Value_NFT_Checker.min_balance} :'
                cprint(text, 'blue')
                spamwriter.writerow([])
                spamwriter.writerow(['', text])
                self.write_small_wallets_to_csv(spamwriter, small_wallets)

            table_view = [[number, wallet, balance] for number, (wallet, balance) in enumerate(self.result.items(), start=1)]
            table = tabulate(table_view, table_head, tablefmt='double_grid')
            self.print_results(total_amount, table)

