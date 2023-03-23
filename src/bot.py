import os
import random
import re

import discord
from discord.ext import commands

from open_ai_chat import send_prompt

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

RANDOM_REPLY_CHANCE = 36

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents)

headers = {'Content-type': 'application/json'}

appId = None

channel_message_history = {}


def add_message_to_history(channel_id, content, name, role="user"):
  text = remove_mentions(content)

  if text == '':
    return False

  if channel_id not in channel_message_history:
    channel_message_history[channel_id] = []

  if role == "user":
    channel_message_history[channel_id].append({"role": "user", "content": f'{name}「{text}」'})
  elif role == "assistant":
    channel_message_history[channel_id].append({"role": "assistant", "content": f'{text}'})
  elif role == "system":
    channel_message_history[channel_id].append({"role": "system", "content": f'{text}'})

  # 5件を超えた場合、最も古いメッセージを削除
  if len(channel_message_history[channel_id]) > 5:
    channel_message_history[channel_id].pop(0)

  return True


def remove_mentions(text):
  # 正規表現でメンション部分を削除
  mention_pattern = r'<@!?[0-9]+>'
  return re.sub(mention_pattern, '', text)


def get_user_nickname(member):
  return member.name if member.nick is None else member.nick


def get_reply(message, gpt_messages=None):
  if gpt_messages is None:
    gpt_messages = channel_message_history[message.channel.id]

  messages = send_prompt(gpt_messages)

  print('response: %s' % messages)

  return messages


async def reply_to(message, gpt_messages=None):
  if gpt_messages is None:
    gpt_messages = channel_message_history[message.channel.id]

  async with message.channel.typing():
    messages = get_reply(message, gpt_messages)

  replyMessage = await message.reply(messages[-1]['content'])

  await wait_reply(replyMessage, messages)


async def wait_reply(message, gpt_messages):
  def check(m):
    return m.reference is not None and m.reference.message_id == message.id

  msg = await bot.wait_for('message', timeout=180.0, check=check)
  gpt_messages.append({"role": "user", "content": f"{get_user_nickname(msg.author)}「{msg.content}」"})

  await reply_to(msg, gpt_messages)


@bot.event
async def on_ready():
  print('ログイン')
  print('Servers connected to:')

  for guild in bot.guilds:
    print(f'{guild.name} {guild.id}')


@bot.event
async def setup_hook():
  # Cogロード
  await bot.load_extension("cogs.chart_cog")
  await bot.load_extension("cogs.proposal_cog")
  await bot.load_extension("cogs.price_cog")

  # コマンド反映
  await bot.tree.sync()


@bot.event
async def on_message(message):
  if message.content.startswith('http') or message.content == '!!':
    return

  yatte = re.match(r'(.*)やって$', message.content)
  if yatte:
    async with message.channel.typing():
      play = yatte.group(1)
      await bot.change_presence(activity=discord.Game(name=play))

    await message.channel.send(f"{play}をプレイするよ")
    return

  # メッセージ履歴にメッセージを追加
  if message.author == bot.user:
    add_message_to_history(message.channel.id, message.content, get_user_nickname(message.author), role="assistant")
  else:
    add_message_to_history(message.channel.id, message.content, get_user_nickname(message.author))

  if str(bot.user.id) in message.content:
    await reply_to(message)
    return

  if random.randint(1, RANDOM_REPLY_CHANCE) == 1 and len(channel_message_history[message.channel.id]) > 2:
    async with message.channel.typing():
      messages = get_reply(message)
      m = await message.channel.send(messages[-1]['content'])

    await wait_reply(m, messages)
    return


@bot.event
async def on_voice_state_update(member, before, after):
  if before.channel == after.channel:
    return

  server = before.channel.guild if after.channel is None else after.channel.guild
  channel = discord.utils.get(server.channels, name='general', type=discord.ChannelType.text)
  name = get_user_nickname(member)

  if after.channel is None:
    async with channel.typing():
      await channel.send(f'{name}が{before.channel.name}からきえてく・・・')
  else:
    async with channel.typing():
      await channel.send(f"{name}が{after.channel.name}に入ったよ")


bot.run(DISCORD_TOKEN)
