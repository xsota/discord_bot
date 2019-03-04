import discord
import random
import os
import requests

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GAME_GATYA_API_URL = os.environ.get('GAME_GATYA_API_URL')

client = discord.Client()


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


client.run(DISCORD_TOKEN)
