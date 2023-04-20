import os

import discord
from discord.ext import commands
from logging import basicConfig, getLogger, INFO
basicConfig(level=INFO)
logger = getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!?!!?', intents=intents)

appId = None


@bot.event
async def setup_hook():
  # Cogロード
  await bot.load_extension("cogs.chart_cog")
  await bot.load_extension("cogs.proposal_cog")
  await bot.load_extension("cogs.price_cog")
  await bot.load_extension("cogs.events_cog")
  await bot.load_extension("cogs.recommended_games_cog")

  # コマンド反映
  await bot.tree.sync()


bot.run(DISCORD_TOKEN)
