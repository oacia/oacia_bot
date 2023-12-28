from telethon import TelegramClient,events
import json

with open("/content/credentials.json", "r") as file:
    credentials = json.loads(file.read())

api_id = credentials["API_ID"]
api_hash = credentials["API_HASH"]
bot_token = credentials["BOT_TOKEN"]
session = credentials["session"]
client = TelegramClient(session, api_id, api_hash).start(bot_token=bot_token)
# Note that 'session_name_file' will be used to save your session (persistent information such as access key and others) as 'session_name_file.session' in your disk. 
# This is by default a database file using Python's sqlite

@client.on(events.NewMessage())
async def readMessages(event):
    # first we get the user information
    user = await client.get_entity(event.peer_id.user_id)
    id = user.id
    name = user.first_name
    lastName = user.last_name
    username = user.username
    if name=='oacia':
        respondMessage = f"hi! my owner ^.^ {name}\nwhat a nice day~"
    else:
        respondMessage=f"hello, {name}"
    #then we send the message back replying the recibed message
    await event.reply(respondMessage)


# Run the event loop to start receiving messages
client.run_until_disconnected()