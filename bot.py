import discord
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

bot = commands.Bot(command_prefix='$')

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
    text = message.content.replace('<@' + str(bot.user.id) + '>', '')
    replyText = getReply(text)

  replyMessage = await message.reply(replyText)

  await waitReply(replyMessage)

async def waitReply(message):
  def check(m):
    return m.reference is not None and m.reference.message_id == message.id

  msg = await bot.wait_for('message',  timeout=180.0, check=check)
  await replyTo(msg)

@bot.event
async def on_ready():
  print('ログイン')


@bot.event
async def on_message(message):
  if message.content.startswith('$'):
    await bot.process_commands(message)

  if message.author == bot.user or message.content.startswith('http'):
    return

  yatte = re.match(r'(.*)やって$', message.content)
  if yatte:
    async with message.channel.typing():
      play = yatte.group(1)
      await bot.change_presence(activity=discord.Game(name=play))

    await message.channel.send(play + 'をプレイするよ')
    return

  if str(bot.user.id) in message.content:
    await replyTo(message)
    return

  if random.randint(1, 6) == 6:
    async with message.channel.typing():
      text = message.content.replace('<@' + str(bot.user.id) + '>', '')
      reply = getReply(text)
      m = await message.channel.send(reply)

    await waitReply(m)


@bot.event
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

@bot.command()
async def add(ctx, a: int, b: int):
  await ctx.send(a + b)

@bot.command()
async def chart(ctx, symbol):
  await ctx.send(f'{symbol}/USDの1時間足のチャートを調べるねっ')

  try:
    index = 1
    ohlcv = exchange.fetch_ohlcv(f'{symbol}/USD', '1h')
    series = [x[index] for x in ohlcv]
    chart = plot(series[-25:], {'height': 15})

    await ctx.send(f'```{chart}```')

  except:
    await ctx.send(f'わかんなかった！')

@bot.command()
async def price(ctx, symbol):
  await ctx.send(f'{symbol}の価格を調べるねっ')

  try:
    ticker = exchange.fetch_ticker(f'{symbol}/USD')

    priceUSDT = (float(ticker['info']['a'][0]) + float(ticker['info']['b'][0])) / 2

    await ctx.send(f'{priceUSDT} USDくらい！')

  except:
    await ctx.send(f'{symbol}わかんない！')


bot.run(DISCORD_TOKEN)
