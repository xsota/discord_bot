import discord
from discord import app_commands
from discord.ext import commands


class ProposalCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="proposal", description="Governance Proposal")
  @app_commands.describe(title="タイトル", description="提案内容")
  async def proposal(self, interaction, title: str, description: str):
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


async def setup(bot: commands.Bot):
  await bot.add_cog(ProposalCog(bot))
