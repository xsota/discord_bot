import discord
import random
import os
import requests
import json
from _datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GAME_GATYA_API_URL = os.environ.get('GAME_GATYA_API_URL')
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


@client.event
async def on_ready():
  print('ログイン')


@client.event
async def on_message(message):
  if message.author == client.user or message.content.startswith('http'):
    return

  if message.content.startswith('ゲームガチャ'):
    game = requests.get(GAME_GATYA_API_URL).text
    reply = game + 'とかどうですか？'
    await message.channel.send(reply)
    return

  if str(client.user.id) in message.content or random.randint(1, 6) == 6:
    text = message.content.replace('<@' + str(client.user.id) + '>', '')
    reply = getReply(text)

    await message.channel.send(reply)


@client.event
async def on_voice_state_update(member, before, after):
  if before == after:
    return

  server = before.channel.guild if after.channel is None else after.channel.guild

  channel = discord.utils.get(server.channels, name='general', type=discord.ChannelType.text)

  name = getUserNickName(member)

  if after.channel is None:
    await channel.send(name + 'が通話からきえてく・・・')
  else:
    await channel.send(name + 'が' + after.channel.name + 'に入ったよ')


client.run(DISCORD_TOKEN)
