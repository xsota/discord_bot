import discord
from discord import app_commands
from discord.ext import commands

import ccxt

exchange = ccxt.kraken()


class PriceCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="price",
                        description="symbolのUSD建ての価格を取得するよ")
  @app_commands.describe(symbol="BTC")
  async def price(self, interaction, symbol: str):
    await interaction.response.defer()

    try:
      ticker = exchange.fetch_ticker(f'{symbol}/USD')

      price_usdt = (float(ticker['info']['a'][0]) + float(ticker['info']['b'][0])) / 2

      await interaction.followup.send(f'{symbol}は今{price_usdt} USDくらい！')

    except:
      await interaction.followup.send(f'{symbol}わかんない！')


async def setup(bot: commands.Bot):
  await bot.add_cog(PriceCog(bot))
