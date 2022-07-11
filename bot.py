import discord
import random
import os
import requests
import re
import ojichat
import json

from _datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
TALK_API_TOKEN = os.environ.get('TALK_API_TOKEN')
ZATUDAN_TOKEN = os.environ.get('ZATUDAN_TOKEN')

client = discord.Client()

headers = {'Content-type': 'application/json'}

appId = None


def getUserNickName(member):
  return member.name if member.nick is None else member.nick


def getReply(text):
  url = 'https://chatbot-api.userlocal.jp/api/chat?message=' + text + '&key=' + ZATUDAN_TOKEN
  result = requests.get(url)
  data = result.json()
  response = data['result']

  print('response: %s' % response)

  return response

async def replyTo(message):
  async with message.channel.typing():
    text = message.content.replace('<@' + str(client.user.id) + '>', '')
    replyText = getReply(text)

  replyMessage = await message.reply(replyText)

  await waitReply(replyMessage)

async def waitReply(message):
  def check(m):
    return m.reference is not None and m.reference.message_id == message.id

  msg = await client.wait_for('message',  timeout=180.0, check=check)
  await replyTo(msg)

@client.event
async def on_ready():
  print('ログイン')


@client.event
async def on_message(message):
  print(message.reference)

  if message.author == client.user or message.content.startswith('http'):
    return

  yatte = re.match(r'(.*)やって$', message.content)
  if yatte:
    async with message.channel.typing():
      play = yatte.group(1)
      await client.change_presence(activity=discord.Game(name=play))

    await message.channel.send(play + 'をプレイするよ')
    return

  if str(client.user.id) in message.content:
    await replyTo(message)
    return

  if random.randint(1, 6) == 6:
    async with message.channel.typing():
      reply = ojichat.generate(name=message.author.display_name, level=2)
      m = await message.channel.send(reply)

    await waitReply(m)

@client.event
async def on_voice_state_update(member, before, after):
  if before.channel == after.channel:
    return

  server = before.channel.guild if after.channel is None else after.channel.guild

  channel = discord.utils.get(server.channels, name='general', type=discord.ChannelType.text)

  name = getUserNickName(member)

  if after.channel is None:
    async with channel.typing():
      await channel.send(name + 'が通話からきえてく・・・')
  else:
    async with channel.typing():
      await channel.send(name + 'が' + after.channel.name + 'に入ったよ')


client.run(DISCORD_TOKEN)
