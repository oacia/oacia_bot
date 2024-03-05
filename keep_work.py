import time
import requests
import os

render_name = os.getenv("RENDER_NAME")
def send_post_request():
    url = f"https://{render_name}.onrender.com/webhook"
    data = {"data": "hello world"}
    requests.post(url, data=data)

print("start keep work!send request each 1 minutes")
while True:
    send_post_request()
    time.sleep(60)