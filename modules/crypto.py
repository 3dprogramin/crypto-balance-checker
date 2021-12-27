import requests as req
import json

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'


class Crypto:
    # get balance of btc address from blockchain.com
    @staticmethod
    def get_btc_balance(address):
        url = f'https://www.blockchain.com/btc/address/{address}'
        r = req.get(url, headers={'User-Agent': USER_AGENT})
        return float(r.text.split('current value of this address is')[1].split(' ')[1])

    # get balance of eth address from blockchain.com
    @staticmethod
    def get_eth_balance(address):
        url = f'https://www.blockchain.com/eth/address/{address}'
        r = req.get(url, headers={'User-Agent': USER_AGENT})
        return float(r.text.split('current value of this address is')[1].split(' ')[1])

    @staticmethod
    # get balance of egld address from elrond explorer
    def get_egld_balance(address):
        url = f'https://api.elrond.com/accounts/{address}'
        r = req.get(url)
        js = json.loads(r.text)
        return float(str(int(js['balance']) / 10).split('e')[0])
