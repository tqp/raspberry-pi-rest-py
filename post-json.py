import time

import requests

api_url_dev = 'http://localhost:5000/api/v1/raspberry/test'
api_url_prod = 'https://server.com/api/v1/raspberry/test'
millis = int(round(time.time() * 1000))
post_object = {'device': 'device', 'key': 'key2', 'value': 'value2', 'timestamp': millis}
headers = {'Content-type': 'application/json'}
response = requests.post(api_url_prod, headers=headers, json=post_object, verify=True)
print(response.text)
