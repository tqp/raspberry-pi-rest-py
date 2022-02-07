import time

import requests
import schedule

api_url_prod = 'https://server.com/api/v1/raspberry/test'


def fetch_bitcoin():
    print("Posting Data Sample")
    millis = int(round(time.time() * 1000))
    post_object = {'device': 'device', 'key': 'key2', 'value': 'value2', 'timestamp': millis}
    headers = {'Content-type': 'application/json'}
    response = requests.post(api_url_prod, headers=headers, json=post_object, verify=True)
    print(response.text)


schedule.every(5).seconds.do(fetch_bitcoin)
while True:
    schedule.run_pending()
    time.sleep(1)
