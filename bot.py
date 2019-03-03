import discord
import random
import os

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
  print('ログイン')


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('ゲームガチャ'):
    game_list = ['オーバーウォッチ', 'モンハン', 'オナニー']
    reply = random.choice(game_list)
    await client.send_message(message.channel, reply)


client.run(DISCORD_TOKEN)
