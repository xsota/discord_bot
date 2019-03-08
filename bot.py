import discord
import random
import os
import requests
import json
import pya3rt

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GAME_GATYA_API_URL = os.environ.get('GAME_GATYA_API_URL')
TALK_API_TOKEN = os.environ.get('TALK_API_TOKEN')

client = discord.Client()
talkClient = pya3rt.TalkClient(TALK_API_TOKEN)


@client.event
async def on_ready():
  print('ログイン')

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
    result = talkClient.talk(text)
    print(text)
    await client.send_message(message.channel, result['results'][0]['reply'])


@client.event
async def on_voice_state_update(before_member, after_member):
  if before_member.voice.voice_channel == after_member.voice.voice_channel:
    return

  server = before_member.voice.voice_channel.server if after_member.voice.voice_channel is None else after_member.voice.voice_channel.server

  channel = channel = discord.utils.get(server.channels, name='general', type=discord.ChannelType.text)

  name = after_member.name if after_member.nick is None else after_member.nick

  if after_member.voice.voice_channel is None:
    await client.send_message(channel, name + 'が通話から出たよ')
  else:
    await client.send_message(channel, name + 'が' + after_member.voice.voice_channel.name + 'に入ったよ')


client.run(DISCORD_TOKEN)
