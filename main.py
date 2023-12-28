from telethon import TelegramClient, events
import json
import re
import requests
import os
from tqdm import tqdm

# 请求头
header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"}
with open("./credentials.json", "r") as file:
    credentials = json.loads(file.read())

api_id = credentials["API_ID"]
api_hash = credentials["API_HASH"]
bot_token = credentials["BOT_TOKEN"]
session = credentials["session"]
proxy = credentials["proxy"]
client = TelegramClient(session, api_id, api_hash, proxy=proxy).start(bot_token=bot_token)


# 抖音视频无水印
async def videos(surl, user):
    # print('正在解析抖音视频链接')
    # 获取video_id （重定向后的链接会变化具体我也没弄清楚就做了两种判断）
    if len(surl) > 60:
        id = re.search(r'video/(\d.*)/', surl).group(1)
    else:
        id = re.search(r'video/(\d.*)', surl).group(1)
    # print(id)
    # 获取json数据
    u_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?item_ids={}&a_bogus=".format(id)
    v_rs = requests.get(url=u_id, headers=header).json()
    # titles = v_rs['item_list'][0]['desc']
    # 截取文案
    titles = re.search(r'^(.*?)[；;。.#]', v_rs['item_list'][0]['desc']).group(1)
    # print(titles)
    # 创建video文件夹
    if not os.path.exists('douyin/video'):
        os.makedirs('douyin/video')
    # 获取uri参数
    req = v_rs['item_list'][0]['video']['play_addr']['uri']
    # print("vvvvvv", req)
    # print('正在下载无水印视频')
    # 下载无水印视频
    v_url = "https://www.douyin.com/aweme/v1/play/?video_id={}".format(req)
    v_req = requests.get(url=v_url, headers=header)
    # print(v_req.headers)
    # 写入文件
    # 拿到文件的长度，并把total初始化为0
    total = int(v_req.headers.get('content-length', 0))
    # 打开当前目录的fname文件(名字你来传入)
    # 初始化tqdm，传入总数，文件名等数据，接着就是写入，更新等操作了
    with open(f'douyin/video/{titles}.mp4', 'wb') as file, tqdm(
            desc=f'{titles}.mp4',
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in v_req.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    print(f"send douyin/video/{titles}.mp4 to {user}")
    await client.send_file(user, f'douyin/video/{titles}.mp4', vedio_note=True)


# 抖音图片无水印
async def pics(surl, user):
    # 获取id
    # if len(surl) > 60:
    #     pid = re.search(r'note/(\d.*)/', surl).group(1)
    # else:
    #     pid = re.search(r'note/(\d.*)', surl).group(1)
    pid = re.search(r'note/(\d+)', surl)
    if pid:
        pid = pid.group(1)
    # 获取json数据
    p_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?reflow_source=reflow_page&item_ids={}&a_bogus=".format(pid)
    # print(p_id)
    p_rs = requests.get(url=p_id, headers=header).json()
    # print(p_rs)
    # 拿到images下的原图片
    images = p_rs['item_list'][0]['images']
    # 获取文案
    ptitle = re.search(r'^(.*?)[；;。.#]', p_rs['item_list'][0]['desc']).group(1).strip()
    # 创建pic文件夹
    if not os.path.exists('douyin/pic'):
        os.makedirs('douyin/pic')
    if not os.path.exists(f'douyin/pic/{ptitle}'):
        os.makedirs(f'douyin/pic/{ptitle}')
    # 下载无水印照片(遍历images下的数据)
    for i, im in enumerate(images):
        # 每一条数据下面都有四个原图链接这边用的是第一个
        p_req = requests.get(url=im['url_list'][0])
        # print(p_req)
        # 保存图片
        # 拿到文件的长度，并把total初始化为0
        total = int(p_req.headers.get('content-length', 0))
        # 打开当前目录的fname文件(名字你来传入)
        # 初始化tqdm，传入总数，文件名等数据，接着就是写入，更新等操作了
        with open(f'douyin/pic/{ptitle}/{str(i + 1)}.jpg', 'wb') as file, tqdm(
                desc=f'{ptitle + str(i + 1)}.jpg',
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in p_req.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        print(f"send douyin/pic/{ptitle}/{str(i + 1)}.jpg to {user}")
        await client.send_file(user, f'douyin/pic/{ptitle}/{str(i + 1)}.jpg')


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await client.get_entity(event.peer_id.user_id)
    response = f"hello!{sender.username}, this is a bot create by oacia\nyou can view source code at https://github.com/oacia/oacia_bot"
    response+=f"\nyou can download douyin vedio or pictures by sending a shared link"
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


# Run the event loop to start receiving messages
client.run_until_disconnected()
