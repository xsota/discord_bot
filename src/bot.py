import os
from logging import basicConfig, getLogger, INFO

import discord
from discord.ext import commands
from langchain_openai import ChatOpenAI

from tools.web_search import web_search

basicConfig(level=INFO)
logger = getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!?!!?', intents=intents)
bot.meowgent = None

appId = None


@bot.event
async def setup_hook():
  from meowgent import Meowgent

  # load llm
  model = ChatOpenAI(
    model=os.environ.get('OPEN_AI_MODEL'),
    openai_api_key=os.environ.get('OPEN_AI_API_KEY'),
    openai_api_base=os.environ.get('OPEN_AI_API_URL'),
    max_tokens=int(os.environ.get('OPEN_AI_MAX_TOKEN')),
    temperature=float(os.environ.get('TEMPERATURE', 1))
  )

  # tools settings
  tools = [web_search]

  # character settings
  character_prompt = os.environ.get('CHARACTER_PROMPT')

  # Meowgent initialize
  bot.meowgent = Meowgent(
    model=model,
    tools=tools,
    system_prompt=character_prompt
  )

  async def on_stamina_change(stamina: int, max_stamina: int):
    """スタミナ変更時に呼び出される処理"""
    logger.info(f"[EventsCog] Meowgent's stamina updated: {stamina}")
    # botのステータスをスタミナに変更
    # Botのステータスを更新
    activity = discord.Game(name=render_stamina_bar(stamina, max_stamina, 10))
    await bot.change_presence(activity=activity)

  def render_stamina_bar(current: int, max_stamina: int, bar_length: int = 20) -> str:
    filled_length = int(bar_length * current / max_stamina)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    return f"[{bar}]"

  bot.meowgent.add_stamina_listener(on_stamina_change)
  bot.meowgent.start_stamina_recovery(interval=360, recovery_amount=1) # 8時間で80くらい回復してほしい

  logger.info("Meowgent instance has been initialized.")

  # Cogロード
  await bot.load_extension("cogs.chart_cog")
  await bot.load_extension("cogs.proposal_cog")
  await bot.load_extension("cogs.price_cog")
  await bot.load_extension("cogs.events_cog")

  # コマンド反映
  await bot.tree.sync()

bot.run(DISCORD_TOKEN)
