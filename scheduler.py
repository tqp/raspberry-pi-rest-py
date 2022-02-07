# REF: https://www.tutorialspoint.com/event-scheduler-in-python

import time

import requests
import schedule

url = "https://api.coindesk.com/v1/bpi/currentprice.json"
data = requests.get(url)
parameters = data.json()


def fetch_bitcoin():
    print("Getting Bitcoin Price")
    result = parameters['bpi']['USD']
    print(result)


def fetch_bitcoin_by_currency(x):
    print("Getting bitcoin price in: ", x)
    result = parameters['bpi'][x]
    print(result)


# time
schedule.every(4).seconds.do(fetch_bitcoin)
schedule.every(7).seconds.do(fetch_bitcoin_by_currency, 'GBP')
schedule.every(9).seconds.do(fetch_bitcoin_by_currency, 'EUR')
while True:
    schedule.run_pending()
    time.sleep(1)
