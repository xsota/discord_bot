import discord
from discord import app_commands
from discord.ext import commands

import random
import os
import requests
import re
import ccxt
import json
from _datetime import datetime
from asciichart import plot


DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
ZATUDAN_TOKEN = os.environ.get('ZATUDAN_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client=discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

headers = {'Content-type': 'application/json'}

appId = None
exchange = ccxt.kraken()


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
  print('Servers connected to:')
  await tree.sync()

  for guild in client.guilds:
    print(f'{guild.name} {guild.id}')

@client.event
async def on_message(message):
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
      text = message.content.replace('<@' + str(client.user.id) + '>', '')
      reply = getReply(text)
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
      await channel.send(f'{name}が{before.channel.name}からきえてく・・・')
  else:
    async with channel.typing():
      await channel.send(name + 'が' + after.channel.name + 'に入ったよ')


@tree.command(description="symbolの1時間足のチャートを調べるねっ")
@app_commands.describe(symbol="BTC")
async def chart(interaction, symbol: str):
  await interaction.response.defer() # 考え中・・・

  try:
    index = 1
    ohlcv = exchange.fetch_ohlcv(f'{symbol}/USD', '1h')
    series = [x[index] for x in ohlcv]
    chart = plot(series[-25:], {'height': 15})

    await interaction.followup.send(f'{symbol}/USD 1h```{chart}```')

  except:
    await interaction.followup.send(f'わかんなかった！')
#

@tree.command(description="symbolのUSD建ての価格を取得するよ")
@app_commands.describe(symbol="BTC")
async def price(interaction, symbol: str):
  await interaction.response.defer()

  try:
    ticker = exchange.fetch_ticker(f'{symbol}/USD')

    price_usdt = (float(ticker['info']['a'][0]) + float(ticker['info']['b'][0])) / 2

    await interaction.followup.send(f'{symbol}は今{price_usdt} USDくらい！')

  except:
    await interaction.followup.send(f'{symbol}わかんない！')

@tree.command(description="Governance Proposal")
@app_commands.describe(title="タイトル",description="提案内容")
async def proposal(interaction, title:str, description: str):
  await interaction.response.defer()
  embed = discord.Embed(title=title,description=description)
  embed.add_field(name="Vote",value="🆗:Yes\n🙅:No \n💤:Abstain\n💢:No with Veto",inline=False)
  # embed.add_field(name="Yes",value="0")
  # embed.add_field(name="No",value="0")
  # embed.add_field(name="Abstain",value="0")
  # embed.add_field(name="No with Veto",value="0")

  message = await interaction.followup.send(embed=embed)
  emoji = "🆗🙅💤💢"

  for i in range(4):
    await message.add_reaction(emoji[i])

client.run(DISCORD_TOKEN)
