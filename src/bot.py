import os

import discord
from discord.ext import commands
from logging import basicConfig, getLogger, INFO

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
  logger.info("Meowgent instance has been initialized.")

  # Cogロード
  await bot.load_extension("cogs.chart_cog")
  await bot.load_extension("cogs.proposal_cog")
  await bot.load_extension("cogs.price_cog")
  await bot.load_extension("cogs.events_cog")

  # コマンド反映
  await bot.tree.sync()

bot.run(DISCORD_TOKEN)
