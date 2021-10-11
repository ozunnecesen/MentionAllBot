import os, logging, asyncio
from telethon import Button
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

api_id = int(os.environ.get("APP_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("TOKEN")
client = TelegramClient('client', api_id, api_hash).start(bot_token=bot_token)
spam_chats = []

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
  await event.reply("__**I'm MentionAll Bot**, I can mention almost all members in group or channel 👻\nClick **/help** for more information__\n\n Follow [@AnjanaMadu](https://github.com/AnjanaMadu) on Github",
                    buttons=(
                      [Button.url('📣 Channel', 'https://t.me/harp_tech'),
                      Button.url('📦 Source', 'https://github.com/AnjanaMadu/MentionAllBot')]
                    ),
                    link_preview=False
                   )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
  helptext = "**Help Menu of MentionAllBot**\n\nCommand: /mentionall\n__You can use this command with text what you want to mention others.__\n`Example: /mentionall Good Morning!`\n__You can you this command as a reply to any message. Bot will tag users to that replied messsage__.\n\nFollow [@AnjanaMadu](https://github.com/AnjanaMadu) on Github"
  await event.reply(helptext,
                    buttons=(
                      [Button.url('📣 Channel', 'https://t.me/harp_tech'),
                      Button.url('📦 Source', 'https://github.com/AnjanaMadu/MentionAllBot')]
                    ),
                    link_preview=False
                   )
  
@client.on(events.NewMessage(pattern="^/mentionall ?(.*)"))
async def mentionall(event):
  if event.is_private:
    return await event.respond("__This command can be use in groups and channels!__")
  
  is_admin = False
  try:
    partici_ = await client(GetParticipantRequest(
      event.chat_id,
      event.sender_id
    ))
  except UserNotParticipantError:
    is_admin = False
  else:
    if (
      isinstance(
        partici_.participant,
        (
          ChannelParticipantAdmin,
          ChannelParticipantCreator
        )
      )
    ):
      is_admin = True
  if not is_admin:
    return await event.respond("__Only admins can mention all!__")
  
  if event.pattern_match.group(1):
    mode = "text_on_cmd"
    msg = event.pattern_match.group(1)
  elif event.reply_to_msg_id:
    mode = "text_on_reply"
    msg = event.reply_to_msg_id
    if msg == None:
        return await event.respond("__I can't mention members for older messages! (messages which are sent before I'm added to group)__")
  elif event.pattern_match.group(1) and event.reply_to_msg_id:
    return await event.respond("__Give me one argument!__")
  else:
    return await event.respond("__Reply to a message or give me some text to mention others!__")
  
  spam_chats.append(event.chat_id)
  if mode == "text_on_cmd":
    usrnum = 0
    usrtxt = ""
    async for usr in client.iter_participants(event.chat_id):
      while event.chat_id in spam_chats:
        usrnum += 1
        usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}) "
        if usrnum == 5:
          await client.send_message(event.chat_id, f"{usrtxt}\n\n{msg}")
          await asyncio.sleep(2)
          usrnum = 0
          usrtxt = ""
        
  if mode == "text_on_reply":
    usrnum = 0
    usrtxt = ""
    async for usr in client.iter_participants(event.chat_id):
      while event.chat_id in spam_chats:
        usrnum += 1
        usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}) "
        if usrnum == 5:
          await client.send_message(event.chat_id, usrtxt, reply_to=msg)
          await asyncio.sleep(2)
          usrnum = 0
          usrtxt = ""

  spam_chats.remove(event.chat_id)

@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
  if not event.chat_id in spam_chats:
    return await event.respond('__There is no proccess on going...__')
  else:
    spam_chats.remove(event.chat_id)
    return await event.respond('__Stopped.__')

print(">> BOT STARTED <<")
client.run_until_disconnected()
