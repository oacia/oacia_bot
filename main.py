from telethon import TelegramClient, events
from telethon.sessions import StringSession
import json
import re
import requests
from io import BytesIO
import os
from flask import Flask, request

# 请求头
header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"}

# # just for my local test...
# config_path = ""
# if os.path.exists('./secret'):
#     config_path = "secret/"
#
# with open(f"{config_path}config.json", "r") as file:
#     credentials = json.loads(file.read())
#
# api_id = credentials["API_ID"]
# api_hash = credentials["API_HASH"]
# bot_token = credentials["BOT_TOKEN"]
# session = credentials["SESSION"]
# proxy = credentials["PROXY"]  # set proxy,eg.["HTTP", "127.0.0.1", 7890]

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
session = os.getenv("SESSION")

app = Flask(__name__)
app.run()
client = TelegramClient('/tmp/oacia_bot', api_id=api_id, api_hash=api_hash)
client.start(bot_token=bot_token)
client.run_until_disconnected()
@app.route('/callback', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    #app.logger.info("receive message")
    client.send_message('oacia', "6666666")
    if request.method == "POST":
        app.logger.info(request.get_json(force=True))
        client.send_message('oacia', "12345678")
        client.send_message('oacia', request.get_json(force=True))
    return 'ok'


# 抖音视频无水印
async def videos(surl, user, event):
    id = re.search(r'video/(\d+)', surl).group(1)
    # print(id)
    # 获取json数据
    u_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?item_ids={}&a_bogus=".format(id)
    v_rs = requests.get(url=u_id, headers=header).json()
    # 获取uri参数
    req = v_rs['item_list'][0]['video']['play_addr']['uri']
    v_url = "https://www.douyin.com/aweme/v1/play/?video_id={}".format(req)
    print(f"{user}: [send] {req}.mp4")
    await event.reply("1 vedio downloading...")
    # 将视频下载的压力转移给gelegram服务器:)
    await client.send_file(user, v_url, video_note=True)


# 抖音图片无水印
async def pics(surl, user, event):
    pid = re.search(r'note/(\d+)', surl).group(1)
    # 获取json数据
    p_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?reflow_source=reflow_page&item_ids={}&a_bogus=".format(pid)
    # print(p_id)
    p_rs = requests.get(url=p_id, headers=header).json()
    # print(p_rs)
    # 拿到images下的原图片
    images = p_rs['item_list'][0]['images']
    await event.reply(f"{len(images)} picture downloading...")
    for i, im in enumerate(images):
        p_req = requests.get(url=im['url_list'][0])
        photo = BytesIO()
        photo.name = 'photo.jpg'
        for data in p_req.iter_content(chunk_size=1024):
            photo.write(data)
        photo.seek(0, 0)
        print(f"{user}: [send] {im['url_list'][0]}")
        await client.send_file(user, photo)


#@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await client.get_entity(event.peer_id.user_id)
    response = f"hello! {sender.username}"
    response += '''
    this is a bot create by oacia
    you can:
    1 - download douyin vedio or pictures by sending a shared link
    
    source code:https://github.com/oacia/oacia_bot'''
    await event.reply(response)


#@client.on(events.NewMessage(pattern=r'.*v\.douyin\.com.*'))
async def readMessages(event):
    user = await client.get_entity(event.peer_id.user_id)
    print(f"{user.username}: [receive] msg{event.text}")
    share = re.search(r'/v.douyin.com/(.*?)/', event.text).group(1)
    # 请求链接
    share_url = "https://v.douyin.com/{}/".format(share)
    s_html = requests.get(url=share_url, headers=header)
    # 获取重定向后的视频id
    surl = s_html.url
    if re.search(r'/video', surl) != None:
        await videos(surl, user.username, event)
        # 判断链接类型为图集分享类型
    elif re.search(r'/note', surl) != None:
        await pics(surl, user.username, event)
# Run the event loop to start receiving messages
#client.run_until_disconnected()
