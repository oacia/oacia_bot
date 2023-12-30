import re
import requests
from io import BytesIO
import os
import asyncio
# from flask import Flask, request
from sanic import Sanic
from sanic.response import json
from telebot.async_telebot import AsyncTeleBot
import telebot
import aiohttp
# 请求头
header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"}

#api_id = int(os.getenv("API_ID"))
#api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
#session = os.getenv("SESSION")
app = Sanic(__name__)
bot = AsyncTeleBot(token=bot_token)
@app.route("/")
async def index():
    return 'hello world'
    # bot.remove_webhook()
    # time.sleep(1)
    # bot.set_webhook(url=os.getenv("URL"))
    #
    # hello = modules.hello()
    # content = modules.content()
    # return render_template("index.html", hello=hello, content=content)

@app.route('/callback', methods=['POST'])
async def callback(request):
    update = telebot.types.Update.de_json(request.json)
    await bot.process_new_updates([update])
    await asyncio.sleep(2)
    return "ok"
# with open(f"secret/config.json", "r") as file:
#     credentials = json.loads(file.read())
# bot_token = credentials["BOT_TOKEN"]


# client = TelegramClient(session=StringSession(session), api_id=api_id, api_hash=api_hash).start(bot_token=bot_token)
# client.connect()

#application = Application.builder().token(bot_token).updater(None).build()
# await application.bot.set_webhook(url=f"{URL}/callback", allowed_updates=Update.ALL_TYPES)


# @app.route('/callback', methods=['POST'])
# def webhook_handler():
#     """Set route /callback with POST method will trigger this method."""
#     if request.method == "POST":
#         update = telegram.Update.de_json(request.get_json(force=True), bot)
#         dispatcher.process_update(update)
#         # application.add_handler(CommandHandler("start", start))
#         # application.add_handler(MessageHandler(filters.Regex(r'.*v\.douyin\.com.*'), douyin))
#         # await application.update_queue.put(Update.de_json(data=request.json, bot=application.bot))
#         # async with application:
#         #     await application.start()
#         #     time.sleep(2)
#         #     await application.stop()
#     return 'ok'
#
# @app.route('/')
# def home():
#     return 'hello world'



# 抖音视频无水印
async def videos(surl, message:telebot.types.Message):
    id = re.search(r'video/(\d+)', surl).group(1)
    # print(id)
    # 获取json数据
    u_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?item_ids={}&a_bogus=".format(id)
    v_rs = requests.get(url=u_id, headers=header).json()
    # 获取uri参数
    req = v_rs['item_list'][0]['video']['play_addr']['uri']
    v_url = "https://www.douyin.com/aweme/v1/play/?video_id={}".format(req)
    #print(f"{user}: [send] {req}.mp4")
    await bot.send_message(message.chat.id,"1 vedio downloading...")
    await bot.send_video(message.chat.id,v_url)
    #update.message.reply_text("1 vedio downloading...")
    #update.message.reply_video(v_url)
    #await event.reply("1 vedio downloading...")
    # 将视频下载的压力转移给gelegram服务器:)
    #await client.send_file(user, v_url, video_note=True)


# 抖音图片无水印
async def pics(surl, message:telebot.types.Message):
    pid = re.search(r'note/(\d+)', surl).group(1)
    # 获取json数据
    p_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?reflow_source=reflow_page&item_ids={}&a_bogus=".format(pid)
    # print(p_id)
    p_rs = requests.get(url=p_id, headers=header).json()
    # print(p_rs)
    # 拿到images下的原图片
    images = p_rs['item_list'][0]['images']
    await bot.send_message(message.chat.id,f"{len(images)} picture downloading...")
    #update.message.reply_text(f"{len(images)} picture downloading...")
    #await event.reply(f"{len(images)} picture downloading...")
    for i, im in enumerate(images):
        p_req = requests.get(url=im['url_list'][0])
        photo = BytesIO()
        photo.name = 'photo.jpg'
        for data in p_req.iter_content(chunk_size=1024):
            photo.write(data)
        photo.seek(0, 0)
        await bot.send_photo(message.chat.id,photo)
        #print(f"{user}: [send] {im['url_list'][0]}")
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(asyncio.wait(asyncio.ensure_future()))
        #asyncio.run(update.message.reply_photo(photo))
        #await client.send_file(user, photo)


#@client.on(events.NewMessage(pattern='/start'))
@bot.message_handler(command=['/start'])
async def start(message:telebot.types.Message):
    response = f"hello! {message.chat.username}"
    response += '''
    this is a bot create by oacia
    you can:
    1 - download douyin vedio or pictures by sending a shared link
    
    source code:https://github.com/oacia/oacia_bot'''
    await bot.send_message(message.chat.id,response)


#@client.on(events.NewMessage(pattern=r'.*v\.douyin\.com.*'))
@bot.message_handler(regexp=r'.*v\.douyin\.com.*')
async def douyin(message:telebot.types.Message):
    #print(f"{user.username}: [receive] msg{update.message.text}")
    share = re.search(r'/v.douyin.com/(.*?)/', message.text).group(1)
    # 请求链接
    share_url = "https://v.douyin.com/{}/".format(share)
    s_html = requests.get(url=share_url, headers=header)
    # 获取重定向后的视频id
    surl = s_html.url
    if re.search(r'/video', surl) != None:
        await videos(surl, message)
        # 判断链接类型为图集分享类型
    elif re.search(r'/note', surl) != None:
        await pics(surl, message)

# dispatcher = Dispatcher(bot, None)
# dispatcher.add_handler(CommandHandler("start", start))
# dispatcher.add_handler(MessageHandler(Filters.regex(r'.*v\.douyin\.com.*'), douyin))


# Run the event loop to start receiving messages
# client.run_until_disconnected()
if __name__ == '__main__':
    app.run()
