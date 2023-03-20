import os
import random
import re

import ccxt
import discord
from discord import app_commands
from playwright.async_api import async_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from asciichart import plot
from open_ai_chat import send_prompt

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

RANDOM_REPLY_CHANCE = 36


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

headers = {'Content-type': 'application/json'}

appId = None
exchange = ccxt.kraken()

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

  msg = await client.wait_for('message', timeout=180.0, check=check)
  await reply_to(msg, gpt_messages)


@client.event
async def on_ready():
  print('ログイン')
  print('Servers connected to:')
  await tree.sync()

  for guild in client.guilds:
    print(f'{guild.name} {guild.id}')


@client.event
async def on_message(message):
  if message.content.startswith('http') or message.content == '':
    return

  yatte = re.match(r'(.*)やって$', message.content)
  if yatte:
    async with message.channel.typing():
      play = yatte.group(1)
      await client.change_presence(activity=discord.Game(name=play))

    await message.channel.send(f"{play}をプレイするよ")
    return

  # メッセージ履歴にメッセージを追加
  if message.author == client.user:
    add_message_to_history(message.channel.id, message.content, get_user_nickname(message.author), role="assistant")
  else:
    add_message_to_history(message.channel.id, message.content, get_user_nickname(message.author))
  print(channel_message_history)

  if str(client.user.id) in message.content:
    await reply_to(message)
    return

  if random.randint(1, RANDOM_REPLY_CHANCE) == 1 and len(channel_message_history[message.channel.id]) > 2:
    async with message.channel.typing():
      messages = get_reply(message)
      m = await message.channel.send(messages[-1]['content'])

    await wait_reply(m, messages)
    return

@client.event
async def on_voice_state_update(member, before, after):
  if before.channel == after.channel:
    return

  server = before.channel.guild if after.channel is None else after.channel.guild
  channel = discord.utils.get(server.channels, name='general', type=discord.ChannelType.text)
  name = get_user_nickname(member)

  if after.channel is None:
    async with channel.typing():
      add_message_to_history(channel.id, f'{name}が{before.channel.name}から消えた', name,"system")
      await channel.send(f'{name}が{before.channel.name}からきえてく・・・')
  else:
    async with channel.typing():
      add_message_to_history(channel.id, f'{name}が{after.channel.name}に参加した', name, "system")
      await channel.send(f"{name}が{after.channel.name}に入ったよ")




@tree.command(description="symbolの1時間足のチャートを調べるねっ")
@app_commands.describe(symbol="BTC")
async def chart(interaction, symbol: str):
  await interaction.response.defer()  # 考え中・・・

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
@app_commands.describe(title="タイトル", description="提案内容")
async def proposal(interaction, title: str, description: str):
  await interaction.response.defer()
  embed = discord.Embed(title=title, description=description)
  embed.add_field(name="Vote", value="🆗:Yes\n🙅:No \n💤:Abstain\n💢:No with Veto", inline=False)
  # embed.add_field(name="Yes",value="0")
  # embed.add_field(name="No",value="0")
  # embed.add_field(name="Abstain",value="0")
  # embed.add_field(name="No with Veto",value="0")

  message = await interaction.followup.send(embed=embed)
  emoji = "🆗🙅💤💢"

  for i in range(4):
    await message.add_reaction(emoji[i])


@tree.command(description='スクリーンショットを撮るよ')
@app_commands.describe(url='URL')
async def screenshot_browser(interaction, url: str):
  await interaction.response.defer()

  try:
    async with async_playwright() as p:
      ctx = await p.chromium.launch(headless=True)
      page = await ctx.new_page()
      page.set_default_navigation_timeout(60000)

      await page.goto(url)
      await page.screenshot(path='ss.png', full_page=True)
      title = await page.title()

      await ctx.close()

      embed = discord.Embed(title=title)
      embed.set_image(url='attachment://ss.png')

      await interaction.followup.send(file=discord.File('ss.png'), embed=embed)

  except PlaywrightTimeoutError:
    await interaction.followup.send(f'時間かかりそうだからやめるね！')
  except:
    await interaction.followup.send(f'しっぱい！')


client.run(DISCORD_TOKEN)
