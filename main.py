import os, json
from time import sleep
from twilio.rest import Client
from dotenv import load_dotenv
import logging as log
import requests as req
load_dotenv()
log.getLogger().setLevel(log.INFO)


# Send SMS message
def send_sms(message):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    phone_number = os.environ['TWILIO_PHONE_NUMBER']
    to = os.environ['SMS_RECEIVER']

    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body=message,
        from_=phone_number,
        to=to
    )

    log.info(f'Message sent: {message.sid}')


# get balance of eth address from etherscan
def get_balance(address, api_key):
    url = f'https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}'
    r = req.get(url)
    js = json.loads(r.text)
    balance = float(str(int(js['result']) / 10).split('e')[0])
    return round(balance, 2)


def run():
    eth_address = os.environ['ETH_ADDRESS']
    api_key = os.environ['ETHERSCAN_API_KEY']

    # print ETH address and current balance
    log.info(f'ETH address: {eth_address}')
    balance = get_balance(eth_address, api_key)
    latest_balance = balance
    log.info(f'Current balance: {balance} ETH')

    k = 0
    # run until balance changes
    while True:
        latest_balance = get_balance(eth_address, api_key)
        # check if balance changed
        if balance != latest_balance:
            # it did, send SMS and show to UI
            pretty_eth_address = eth_address[0:6] + '...' + eth_address[-4:len(eth_address)]
            msg = f'[ETH bot] Balance changed from {balance} ETH to {latest_balance} ETH for {pretty_eth_address}'
            log.info(msg)
            send_sms(msg)
            # return, no need to continue
            return
        sleep(1)
        k += 1
        # print to UI every 20k checks
        if k % 20000 == 0:
            log.info(f'Checked {k} times')


def main():
    ctrl_c = False
    success = False
    try:
        log.info('ETH balance checker')
        run()
        success = True
    except Exception as ex:
        log.error(ex)
    except KeyboardInterrupt:
        log.warning('CTR+C pressed, stopping')
        ctrl_c = True
    finally:
        # if success or CTRL+C pressed, return
        if success or ctrl_c:
            return

        # if other error, sleep for 30 and restart
        log.info('Sleeping for 30s and restarting')
        sleep(30)
        main()

if __name__ == "__main__":
    main()
