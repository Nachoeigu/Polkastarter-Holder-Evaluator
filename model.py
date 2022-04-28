from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta
from constants import STAKING_ADDRES_POLS_BSCAN, STAKING_ADDRES_POLS_ETHERSCAN, CONTRACT_ID_BSCAN, CONTRACT_ID_ETHERSCAN, WEI, CLOSE_INSCRIPTION_DATE
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
            url = f'https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={CONTRACT_ID_BSCAN}&address={address}&page=1&offset=10000&startblock=0&endblock=999999999&sort=asc&apikey={self.PRIVATE_KEY_BSCAN}'
            data = requests.get(url)
            data = json.loads(data.content)

        else:
            url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={CONTRACT_ID_ETHERSCAN}&address={address}&page=1&offset=10000&startblock=0&endblock=27025780&sort=asc&apikey={self.PRIVATE_KEY_ETHERSCAN}"
            data = requests.get(url)
            data = json.loads(data.content)

        return data

    #With this function we know the total balance of the holder, seven days before the whitelist close
    def balance_of_each_address(self, data, address):
        balance = []
        for transaction in reversed(data['result']):
            transaction_date = datetime.fromtimestamp(int(transaction['timeStamp']))
            if transaction_date > CLOSE_INSCRIPTION_DATE - timedelta(days = 7):
                #The transactions is after seven days of staking
                continue

            transaction_value = int(transaction['value'])/WEI
            receiver = transaction['to']
            sender = transaction['from']
            #If the desired address withdraw tokens
            if sender == address:
                output_transaction = transaction_value*-1
                balance.append(float(output_transaction))
            else:
                input_transaction = transaction_value
                balance.append(float(input_transaction))
            
        return balance

    def request_staking_contract(self, mode:bool, address):
        #mode = True is Bscan
        #mode = False is Etherscan

        if mode == True:
            url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={CONTRACT_ID_BSCAN}&address={address}&page=1&offset=10000&startblock=0&endblock=999999999&sort=asc&apikey={self.PRIVATE_KEY_BSCAN}"
            data = requests.get(url)
            data = json.loads(data.content)

            return data

        else:
            url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={CONTRACT_ID_ETHERSCAN}&address={address}&page=1&offset=10000&startblock=0&endblock=999999999&sort=asc&apikey={self.PRIVATE_KEY_ETHERSCAN}"
            data = requests.get(url)
            data = json.loads(data.content)
            content = []

            return data

    def balance_of_each_transaction(self, mode:bool, data):
        if mode == True:
            bsc_sent = []
            bsc_received = []
            for element in data['result']:
                if datetime.fromtimestamp(int(element['timeStamp'])) > CLOSE_INSCRIPTION_DATE:
                    continue
                elif element['to'] == STAKING_ADDRES_POLS_BSCAN:
                    bsc_sent.append(int(element['value'])/WEI)
                elif element['from'] == STAKING_ADDRES_POLS_BSCAN:
                    bsc_received.append(int(element['value'])/WEI)

            total_staked = (sum(bsc_sent) + sum(bsc_received))
            
            return float(total_staked)

        else:
            eth_sent = []
            eth_received = []
            for element in data['result']:
                if datetime.fromtimestamp(int(element['timeStamp'])) > CLOSE_INSCRIPTION_DATE:
                    continue
                elif element['to'] == STAKING_ADDRES_POLS_ETHERSCAN:
                    eth_sent.append(int(element['value'])/WEI)
                elif element['from'] == STAKING_ADDRES_POLS_ETHERSCAN:
                    eth_received.append(int(element['value'])/WEI)

            total_staked = sum(eth_sent) + sum(eth_received)

            return float(total_staked)

    #This function makes everything happen so we analyze each winner address
    def analyzing_holders(self, list_addresses:list):
        for address in list_addresses:
            time.sleep(1)
            bscan_data = self.request_server(True, address)
            bscan_balance = self.balance_of_each_address(bscan_data, address)

            etherscan_data = self.request_server(False, address)
            etherscan_balance = self.balance_of_each_address(etherscan_data, address)
            total_balance = sum(bscan_balance) + sum(etherscan_balance)

            bscan_data = self.request_staking_contract(True, address)
            bscan_balance = self.balance_of_each_transaction(True, bscan_data)

            etherscan_data = self.request_staking_contract(False, address)
            etherscan_balance = self.balance_of_each_transaction(False, etherscan_data)

            total_balance = bscan_balance + etherscan_balance + total_balance

            print(f"The address {address} held {str(total_balance)} before the inscription closes")
                
