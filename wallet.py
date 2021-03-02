import os
from dotenv import load_dotenv

import subprocess
import json
from constants import *


from web3 import Web3
from web3.auto.gethdev import w3
from web3.middleware import geth_poa_middleware

from eth_account import Account

from bit import wif_to_key
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI

load_dotenv()

mnemonic = os.getenv('MNEMONIC')

def derive_wallets(coin):
    command = f'./derive -g --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey --format=json --coin="{coin}" --numderive=3'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

coins = {
    ETH: derive_wallets(ETH),
    BTCTEST: derive_wallets(BTCTEST)
}
print(coins)


print(coins[ETH][0]['privkey'])
print(coins[BTCTEST][0]['privkey'])

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)



def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": to, "value": amount}
        )
        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
        }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, to, amount):
    raw_tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(raw_tx)
    if coin == ETH: 
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    elif coin == BTCTEST: 
        return NetworkAPI.broadcast_tx_testnet(signed_tx) 
   


Account_one = priv_key_to_account(BTCTEST, coins[BTCTEST][0]['privkey'])
Account_two= coins[BTCTEST][1]['address']