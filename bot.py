import discord
import random
import os
import requests
import json
from _datetime import datetime

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GAME_GATYA_API_URL = os.environ.get('GAME_GATYA_API_URL')
TALK_API_TOKEN = os.environ.get('TALK_API_TOKEN')
DOCOMO_ZATUDAN_TOKEN = os.environ.get('DOCOMO_ZATUDAN_TOKEN')

client = discord.Client()

headers = {'Content-type': 'application/json'}

appId = None


def register():
  url = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/registration?APIKEY=' + DOCOMO_ZATUDAN_TOKEN

  pay = {
    'botId': 'Chatting',
    'appKind': 'unko'
  }
  r = requests.post(url, data=json.dumps(pay), headers=headers)
  appId = r.json()['appId']
  return appId

def getReply(appId, utt_content):
  url = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue?APIKEY=' + DOCOMO_ZATUDAN_TOKEN
  payload = {
    'language': 'ja-JP',
    'botId': 'Chatting',
    'appId': appId,
    'voiceText': utt_content,
    'appRecvTime': '2011-01-11 22:22:22',
    'appSendTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'clientData': {
      'option': {
        'sex':'女',
      }
    }
  }
  result = requests.post(url, data=json.dumps(payload), headers=headers)
  data = result.json()
  response = data['systemText']['expression']

  print('response: %s' % response)
  return response


@client.event
async def on_ready():
  print('ログイン')
  global appId
  appId = register() #とりあえず共通にしとくけどするけどいつかサーバ毎で分けたい

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('ゲームガチャ'):
    game = requests.get(GAME_GATYA_API_URL).text
    reply = game + 'とかどうですか？'
    await client.send_message(message.channel, reply)
    return

  if client.user.id in message.content or random.randint(1,6) == 6:
    text = message.content.replace('<@'+client.user.id+'>', '')
    reply = getReply(appId, text)

    await client.send_message(message.channel, reply)

@client.event
async def on_voice_state_update(before_member, after_member):
  if before_member.voice.voice_channel == after_member.voice.voice_channel:
    return

  server = before_member.voice.voice_channel.server if after_member.voice.voice_channel is None else after_member.voice.voice_channel.server

  channel = discord.utils.get(server.channels, name='general', type=discord.ChannelType.text)

  name = after_member.name if after_member.nick is None else after_member.nick

  if after_member.voice.voice_channel is None:
    await client.send_message(channel, name + 'が通話から出たよ')
  else:
    await client.send_message(channel, name + 'が' + after_member.voice.voice_channel.name + 'に入ったよ')


client.run(DISCORD_TOKEN)
