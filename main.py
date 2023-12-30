import re
import requests
from io import BytesIO
import os

from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters,CommandHandler
import telegram
# 请求头
header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"}

#api_id = int(os.getenv("API_ID"))
#api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
#session = os.getenv("SESSION")
app = Flask(__name__)
bot = telegram.Bot(token=bot_token)
# with open(f"secret/config.json", "r") as file:
#     credentials = json.loads(file.read())
# bot_token = credentials["BOT_TOKEN"]


# client = TelegramClient(session=StringSession(session), api_id=api_id, api_hash=api_hash).start(bot_token=bot_token)
# client.connect()

#application = Application.builder().token(bot_token).updater(None).build()
# await application.bot.set_webhook(url=f"{URL}/callback", allowed_updates=Update.ALL_TYPES)


@app.route('/callback', methods=['POST'])
def webhook_handler():
    """Set route /callback with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        # application.add_handler(CommandHandler("start", start))
        # application.add_handler(MessageHandler(filters.Regex(r'.*v\.douyin\.com.*'), douyin))
        # await application.update_queue.put(Update.de_json(data=request.json, bot=application.bot))
        # async with application:
        #     await application.start()
        #     time.sleep(2)
        #     await application.stop()
    return 'ok'

@app.route('/')
def home():
    return 'hello world'



# 抖音视频无水印
def videos(surl, update):
    id = re.search(r'video/(\d+)', surl).group(1)
    # print(id)
    # 获取json数据
    u_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?item_ids={}&a_bogus=".format(id)
    v_rs = requests.get(url=u_id, headers=header).json()
    # 获取uri参数
    req = v_rs['item_list'][0]['video']['play_addr']['uri']
    v_url = "https://www.douyin.com/aweme/v1/play/?video_id={}".format(req)
    #print(f"{user}: [send] {req}.mp4")
    update.message.reply_text("1 vedio downloading...")
    update.message.reply_video(v_url)
    #await event.reply("1 vedio downloading...")
    # 将视频下载的压力转移给gelegram服务器:)
    #await client.send_file(user, v_url, video_note=True)


# 抖音图片无水印
def pics(surl, update):
    pid = re.search(r'note/(\d+)', surl).group(1)
    # 获取json数据
    p_id = "https://m.douyin.com/web/api/v2/aweme/iteminfo/?reflow_source=reflow_page&item_ids={}&a_bogus=".format(pid)
    # print(p_id)
    p_rs = requests.get(url=p_id, headers=header).json()
    # print(p_rs)
    # 拿到images下的原图片
    images = p_rs['item_list'][0]['images']
    update.message.reply_text(f"{len(images)} picture downloading...")
    #await event.reply(f"{len(images)} picture downloading...")
    photos = []
    for i, im in enumerate(images):
        p_req = requests.get(url=im['url_list'][0])
        photo = BytesIO()
        photo.name = 'photo.jpg'
        for data in p_req.iter_content(chunk_size=1024):
            photo.write(data)
        photo.seek(0, 0)
        photos.append(photo)
        #print(f"{user}: [send] {im['url_list'][0]}")
    update.message.reply_photo(photos)
        #await client.send_file(user, photo)


#@client.on(events.NewMessage(pattern='/start'))
def start(bot, update):
    user = update.effective_user
    response = f"hello! {user.username}"
    response += '''
    this is a bot create by oacia
    you can:
    1 - download douyin vedio or pictures by sending a shared link
    
    source code:https://github.com/oacia/oacia_bot'''
    update.message.reply_text(response)


#@client.on(events.NewMessage(pattern=r'.*v\.douyin\.com.*'))
def douyin(bot, update):
    user = update.effective_user
    print(f"{user.username}: [receive] msg{update.message.text}")
    share = re.search(r'/v.douyin.com/(.*?)/', update.message.text).group(1)
    # 请求链接
    share_url = "https://v.douyin.com/{}/".format(share)
    s_html = requests.get(url=share_url, headers=header)
    # 获取重定向后的视频id
    surl = s_html.url
    if re.search(r'/video', surl) != None:
        videos(surl, update)
        # 判断链接类型为图集分享类型
    elif re.search(r'/note', surl) != None:
        pics(surl, update)

dispatcher = Dispatcher(bot, None)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.regex(r'.*v\.douyin\.com.*'), douyin))


# Run the event loop to start receiving messages
# client.run_until_disconnected()
if __name__ == '__main__':
    app.run()
