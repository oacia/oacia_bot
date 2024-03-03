import time
import requests

def send_post_request():
    url = "http://0.0.0.0:10000/webhook"
    data = {"data": "hello world"}
    requests.post(url, data=data)

print("start keep work!send request each 1 minutes")
while True:
    send_post_request()
    time.sleep(60)