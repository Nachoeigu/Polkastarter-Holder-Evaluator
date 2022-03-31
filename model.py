from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta
from constants import CONTRACT_ID_BSCAN, CONTRACT_ID_ETHERSCAN, WEI, CLOSE_INSCRIPTION_DATE
import time
import os

class Holder_Evaluator:

    def __init__(self):
        load_dotenv()
        #We import the private keys for connection with the blockchain
        self.PRIVATE_KEY_BSCAN = os.getenv("private_key_bscan")
        self.PRIVATE_KEY_ETHERSCAN = os.getenv("private_key_etherscan")

    #With this function we retrieve information from the blockchain of each specific holder
    def request_server(self, mode:bool, address):
        #mode = True is Bscan
        #mode = False is Etherscan
        if mode == True:
            url = f'https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={CONTRACT_ID_BSCAN}&address={address}&page=1&offset=5&startblock=0&endblock=999999999&sort=asc&apikey={self.PRIVATE_KEY_BSCAN}'
            data = requests.get(url)
            data = json.loads(data.content)

        else:
            url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={CONTRACT_ID_ETHERSCAN}&address={address}&page=1&offset=100&startblock=0&endblock=27025780&sort=asc&apikey={self.PRIVATE_KEY_ETHERSCAN}"
            data = requests.get(url)
            data = json.loads(data.content)

        return data

    #With this function we know the total balance of the holder, seven days before the whitelist close
    def balance_of_each_address(self, data, address):
        balance = []
        for transaction in reversed(data['result']):
            transaction_date = datetime.fromtimestamp(int(transaction['timeStamp']))
            if transaction_date > CLOSE_INSCRIPTION_DATE - timedelta(days = 7):
                print("The transactions is after seven days of staking")
                continue

            transaction_value = int(transaction['value'])/WEI
            receiver = transaction['to']
            sender = transaction['from']
            #If the desired address withdraw tokens
            if sender == address:
                output_transaction = transaction_value*-1
                balance.append(output_transaction)
            else:
                input_transaction = transaction_value
                balance.append(input_transaction)
            
        return balance

    #This function makes everything happen so we analyze each winner address
    def analyzing_holders(self, list_addresses:list):
        for address in list_addresses:
            time.sleep(1)
            bscan_data = self.request_server(True, address)
            bscan_balance = self.balance_of_each_address(bscan_data, address)

            etherscan_data = self.request_server(False, address)
            etherscan_balance = self.balance_of_each_address(etherscan_data, address)
            
            print(f"Address {address} = {(sum(etherscan_balance))} + {(sum(bscan_balance))}")
