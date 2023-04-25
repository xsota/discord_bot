import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View

from igdb import search_games_by_theme_ids, get_themes

from open_ai_chat import send_prompt


class ThemeSelect(Select):
  async def callback(self, interaction: discord.Interaction):
    theme_ids = [int(theme_id) for theme_id in self.values]
    games = search_games_by_theme_ids(theme_ids)

    # ゲームのリストを作成する
    game_list = "\n".join([game["name"] for game in games])

    # 時間かかりそうなので返事延期
    await interaction.response.defer()

    # 回答生成
    messages = send_prompt(messages=[
      {"role": "user", "content": f"{interaction.user.name}「おすすめのゲームが知りたくて好きなゲームジャンルを確認しそのジャンルから調べたゲームリストが{game_list}だったので、それを使いゲームをおすすめてしてください」"}
    ])

    await interaction.followup.send(messages[-1]['content'])


class RecommendedGamesCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.themes = get_themes()


  @app_commands.command(name="recommended_games", description="おすすめのゲームを聞く")
  @app_commands.describe()
  async def recommended_games(self, interaction):
    await interaction.response.defer()

    # セレクトメニューのオプションを作成する
    theme_select = ThemeSelect(
      placeholder='気になるゲームジャンルを選択',
      options=[
        discord.SelectOption(label=theme["name"], value=str(theme["id"])) for theme in self.themes
      ],
      min_values=1,
      max_values=4
    )

    # セレクトメニューを作成する
    view = View()
    view.add_item(theme_select)

    await interaction.followup.send('好きなジャンルを選んで！', view=view)


async def setup(bot: commands.Bot):
  await bot.add_cog(RecommendedGamesCog(bot))
