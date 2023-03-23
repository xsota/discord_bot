import discord
from discord import app_commands
from discord.ext import commands
import ccxt
from asciichart import plot

exchange = ccxt.kraken()


class ChartCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
    name="chart",
    description="symbolのUSD建ての価格を取得するよ"
  )
  @app_commands.describe(symbol="BTC")
  async def chart(self, interaction: discord.Interaction, symbol: str):
    await interaction.response.defer()

    try:
      index = 1
      ohlcv = exchange.fetch_ohlcv(f'{symbol}/USD', '1h')
      series = [x[index] for x in ohlcv]
      chart = plot(series[-25:], {'height': 15})

      await interaction.followup.send(f'{symbol}/USD 1h```{chart}```')

    except:
      await interaction.followup.send(f'わかんなかった！')


async def setup(bot: commands.Bot):
  await bot.add_cog(ChartCog(bot))
