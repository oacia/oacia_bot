import asyncio
import aiohttp
from telethon import TelegramClient, events
import json
import re
import requests
import os
from io import BytesIO
import random
import string

# 请求头

DEBUG = False  # 区分远程环境和调试环境

if not DEBUG:
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")
    render_name = os.getenv("RENDER_NAME")
    session = "oacia_bot"
    proxy = None
    cookie = os.getenv("COOKIE")
    if render_name:
        requests.post(f"https://api.telegram.org/bot{bot_token}/setWebhook?url=https://{render_name}.onrender.com/webhook")
        if requests.status_codes == 200:
            print("set webhook successful")
else:
    with open("secret/config.json", "r") as file:
        config = json.loads(file.read())

    api_id = config["API_ID"]
    api_hash = config["API_HASH"]
    bot_token = config["BOT_TOKEN"]
    session = config["SESSION"]
    proxy = config["PROXY"]
    cookie = config["COOKIE"]

header = {
    "Referer": "https://www.douyin.com/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36",
    "Cookie": cookie,
}

client = TelegramClient(session, api_id, api_hash, proxy=proxy).start(bot_token=bot_token)


# 抖音视频下载
async def videos(surl, user):
    id = re.search(r'video/(\d+)', surl).group(1)
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "aweme_id": id,
        "pc_client_type": "1",
        "version_code": "190500",
        "version_name": "19.5.0",
        "cookie_enabled": "true",
        "platform": "PC",
        "downlink": "10",
    }
    note_api = "https://www.douyin.com/aweme/v1/web/aweme/detail/"
    try:
        v_rs = requests.get(url=note_api, headers=header, params=params).json()
    except:
        await client.send_message(user, "cookie失效啦!!")
        return
    # 获取uri参数
    req = v_rs["aweme_detail"]['video']['play_addr']['uri']
    # 下载无水印视频
    v_url = f"https://www.douyin.com/aweme/v1/play/?video_id={req}"
    await client.send_message(user, f"1 vedio sending...\ndownload link: {v_url}",link_preview=False)
    await client.send_file(user, v_url, vedio_note=True)


# 抖音图片无水印
async def pics(surl, user):
    pid = re.search(r'note/(\d+)', surl).group(1)
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "aweme_id": pid,
        "pc_client_type": "1",
        "version_code": "190500",
        "version_name": "19.5.0",
        "cookie_enabled": "true",
        "platform": "PC",
        "downlink": "10",
    }
    note_api = "https://www.douyin.com/aweme/v1/web/aweme/detail/"
    try:
        p_rs = requests.get(url=note_api, headers=header,params=params).json()
    except:
        await client.send_message(user, "cookie失效啦!!")
        return
    # 拿到images下的原图片
    images = p_rs["aweme_detail"]["images"]
    await client.send_message(user, f"{len(images)} photos sending...")
    for i, im in enumerate(images):
        p_req = requests.get(url=im['url_list'][0])
        if p_req.status_code == 200:
            photo = BytesIO()
            photo.name = f'{pid}_{i + 1}.jpg'
            for data in p_req.iter_content(chunk_size=1024):
                photo.write(data)
            photo.seek(0, 0)
            print(f"{user}: [send] {im['url_list'][0]}")
            await client.send_file(user, photo, force_document=True)
        else:
            await client.send_message(user, f"No.{i + 1} picture is facing {p_req.status_code} error!")
            await client.send_file(user, im['url_list'][0])


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await client.get_entity(event.peer_id.user_id)
    response = f"hello! {sender.username}, this is a bot created by @oacia"
    response += '''
    now the bot has these features:
        - download douyin vedio or pictures by sending a shared link
    have a good time!
    source code: https://github.com/oacia/oacia_bot
    tutorial: https://oacia.dev/telegram-bot-develop
    you can deploy this bot by yourself~
    '''
    await event.reply(response)

@client.on(events.NewMessage(pattern=r'.*v\.douyin\.com.*'))
async def readMessages(event):
    user = await client.get_entity(event.peer_id.user_id)
    print(f"{user.username}: receive msg{event.text}")
    share = re.search(r'/v.douyin.com/(.*?)/', event.text)
    if share:
        share = share.group(1)
    else:
        event.reply("not a vaild douyin share link")
    # 请求链接
    share_url = "https://v.douyin.com/{}/".format(share)
    s_html = requests.get(url=share_url, headers=header)
    # 获取重定向后的视频id
    surl = s_html.url
    if re.search(r'/video', surl) is not None:
        await videos(surl, user.username)
        # 判断链接类型为图集分享类型
    elif re.search(r'/note', surl) is not None:
        await pics(surl, user.username)


import subprocess


# 在render部署需要一个端口开放http服务,否则部署将会失败
# 由于client.run_until_disconnected()和flask的app.run(host='0.0.0.0', port=10000)
# 都会阻塞进程,而render只能运行一个python 命令,所以这是取巧的做法, but it works well
def run_flask():
    subprocess.Popen(["python", "for_render.py"])
    subprocess.Popen(["python", "keep_work.py"])


if __name__ == "__main__":
    print("for_render.py start")
    run_flask()
    print('tg bot start')
    client.run_until_disconnected()
