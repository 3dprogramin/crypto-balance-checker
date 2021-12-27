import os
from time import sleep
from twilio.rest import Client
from dotenv import load_dotenv
from modules.crypto import Crypto
from modules.log import Log
load_dotenv()


# get cryptocurrency from environment variables
CRYPTOCURRENCY = os.environ['CRYPTOCURRENCY'].upper()
# setup logging with cryptocurrency
log = Log(CRYPTOCURRENCY)
# set recheck delay
RECHECK_DELAY = int(os.environ['RECHECK_DELAY'])


# Send SMS message
def send_sms(message):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    phone_number = os.environ['TWILIO_PHONE_NUMBER']
    to = os.environ['TWILIO_SMS_RECEIVER']

    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body=message,
        from_=phone_number,
        to=to
    )

    log.info(f'Message sent: {message.sid}')


# main checking method
def run(address, get_balance_method):
    # print ETH address and current balance
    log.info(f'Address: {address}')

    initial_balance = get_balance_method(address)
    log.info(f'Current balance: {format(initial_balance, "f")} {CRYPTOCURRENCY}')

    k = 0
    # run until balance changes
    while True:
        latest_balance = get_balance_method(address)
        # check if balance changed
        if initial_balance != latest_balance:
            # it did, send SMS and show to UI
            pretty_eth_address = address[0:6] + '...' + address[-4:len(address)]
            msg = f'[{CRYPTOCURRENCY}] Balance changed from {format(initial_balance, "f")} {CRYPTOCURRENCY} ' \
                  f'to {format(latest_balance, "f")} {CRYPTOCURRENCY} for {pretty_eth_address}'
            log.info(msg)
            send_sms(msg)
            # return, no need to continue
            return
        sleep(RECHECK_DELAY)
        k += 1
        # print to UI every 20k checks
        if k % 20000 == 0:
            log.info(f'Checked {k} times')


def main():
    ctrl_c = False
    success = False
    unknown_currency = False
    try:
        log.info('Balance checker')
        log.info(f'Re-checking every {RECHECK_DELAY}s')
        # validate currency and set method for getting balance
        if CRYPTOCURRENCY == 'BTC':
            get_balance_method = Crypto.get_btc_balance
        elif CRYPTOCURRENCY == 'ETH':
            get_balance_method = Crypto.get_eth_balance
        elif CRYPTOCURRENCY == 'EGLD':
            get_balance_method = Crypto.get_egld_balance
        else:
            unknown_currency = True
            raise Exception(f'unknown cryptocurrency: {CRYPTOCURRENCY}')

        # start the checking with address as param
        run(os.environ['ADDRESS'], get_balance_method)
        success = True
    except Exception as ex:
        log.error(f'Error: {ex}')
    except KeyboardInterrupt:
        log.warning('CTR+C pressed, stopping')
        ctrl_c = True
    finally:
        # if success or CTRL+C pressed, return
        if success or ctrl_c or unknown_currency:
            return

        # if other error, sleep for 30 and restart
        log.info('Sleeping for 30s and restarting')
        sleep(30)
        main()

if __name__ == "__main__":
    main()
