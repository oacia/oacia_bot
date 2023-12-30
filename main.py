import asyncio

from telethon import TelegramClient, events
import json
import re
import requests
import os
from io import BytesIO

# 请求头
header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"}
# with open("secret/config.json", "r") as file:
#     config = json.loads(file.read())
#
# api_id = config["API_ID"]
# api_hash = config["API_HASH"]
# bot_token = config["BOT_TOKEN"]
# session = config["SESSION"]
# proxy = config["PROXY"]

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
session = "oacia_bot"
proxy = None
client = TelegramClient(session, api_id, api_hash, proxy=proxy).start(bot_token=bot_token)


# 抖音视频无水印
async def videos(surl, user):
    id = re.search(r'video/(\d+)', surl).group(1)
    # print(id)
    # 获取json数据
    u_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?item_ids={}&a_bogus=".format(id)
    v_rs = requests.get(url=u_id, headers=header).json()
    # 获取uri参数
    req = v_rs['item_list'][0]['video']['play_addr']['uri']
    # 下载无水印视频
    v_url = "https://www.douyin.com/aweme/v1/play/?video_id={}".format(req)
    print(f"send douyin/video/{req}.mp4 to {user}")
    await client.send_file(user, v_url, vedio_note=True)


# 抖音图片无水印
async def pics(surl, user):
    # 获取id
    # if len(surl) > 60:
    #     pid = re.search(r'note/(\d.*)/', surl).group(1)
    # else:
    #     pid = re.search(r'note/(\d.*)', surl).group(1)
    pid = re.search(r'note/(\d+)', surl).group(1)
    # if pid:
    #     pid = pid.group(1)
    # 获取json数据
    p_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?reflow_source=reflow_page&item_ids={}&a_bogus=".format(pid)
    # print(p_id)
    p_rs = requests.get(url=p_id, headers=header).json()
    # print(p_rs)
    # 拿到images下的原图片
    images = p_rs['item_list'][0]['images']
    for i, im in enumerate(images):
        p_req = requests.get(url=im['url_list'][0])
        photo = BytesIO()
        photo.name = 'photo.jpg'
        for data in p_req.iter_content(chunk_size=1024):
            photo.write(data)
        photo.seek(0, 0)
        print(f"{user}: [send] {im['url_list'][0]}")
        await client.send_file(user, photo)


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await client.get_entity(event.peer_id.user_id)
    response = f"hello!{sender.username}, this is a bot create by oacia\nyou can view source code at https://github.com/oacia/oacia_bot"
    response += f"\nyou can download douyin vedio or pictures by sending a shared link"
    await event.reply(response)


@client.on(events.NewMessage(pattern=r'.*v\.douyin\.com.*'))
async def readMessages(event):
    user = await client.get_entity(event.peer_id.user_id)
    print(f"{user.username}: receive msg{event.text}")
    share = re.search(r'/v.douyin.com/(.*?)/', event.text)
    if share:
        share = share.group(1)
    else:
        event.reply("not a vaild douyin link")
    # 请求链接
    share_url = "https://v.douyin.com/{}/".format(share)
    s_html = requests.get(url=share_url, headers=header)
    # 获取重定向后的视频id
    surl = s_html.url
    if re.search(r'/video', surl) != None:
        await videos(surl, user.username)
        # 判断链接类型为图集分享类型
    elif re.search(r'/note', surl) != None:
        await pics(surl, user.username)


# render必须得起一个http服务,否则就会断开连接....
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "hello world"

async def main():
    print("start tg bot")
    await client.run_until_disconnected()


if __name__=="__main__":
    asyncio.run(main())
    print("start flask")
    app.run(host='0.0.0.0', port=10000)



