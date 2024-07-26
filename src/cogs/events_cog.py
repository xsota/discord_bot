import discord
from discord.ext import commands
import re
from open_ai_chat import send_prompt
import random
from logging import getLogger

logger = getLogger(__name__)


def remove_mentions(text):
  # 正規表現でメンション部分を削除
  mention_pattern = r'<@!?[0-9]+>'
  return re.sub(mention_pattern, '', text)


def get_user_nickname(member):
  return member.name if member.nick is None else member.nick


class EventsCog(commands.Cog):
  MAX_HISTORY_LENGTH = 10
  RANDOM_REPLY_CHANCE = 36
  channel_message_history = {}

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    logger.info('ログイン')
    logger.info(self.bot.user.id)
    logger.info('Servers connected to:')

    for guild in self.bot.guilds:
      logger.info(f'{guild.name} {guild.id}')

  @commands.Cog.listener()
  async def on_message(self, message):
    # メッセージ履歴にメッセージを追加
    if message.author == self.bot.user:
      self.add_message_to_history(message,role="assistant")
    else:
      self.add_message_to_history(message)

    # メッセージがbot自身からのものであれば、何もしない
    if message.author.id == self.bot.user.id:
      return

    if str(self.bot.user.id) in message.content:
      await self.reply_to(message)
      return

    if random.randint(1, self.RANDOM_REPLY_CHANCE) == 1 and len(self.channel_message_history[message.channel.id]) > 2:
      async with message.channel.typing():
        messages = self.get_reply(message)
        m = await message.channel.send(messages[-1].content)

      await self.wait_reply(m, messages)
      return

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    if before.channel == after.channel:
      return

    server = before.channel.guild if after.channel is None else after.channel.guild
    channel = discord.utils.get(server.channels, name='general', type=discord.ChannelType.text)
    name = get_user_nickname(member)

    if after.channel is None:
      async with channel.typing():
        await channel.send(f'{name}が{before.channel.name}からきえてくにゃ・・・')
    else:
      async with channel.typing():
        await channel.send(f"{name}が{after.channel.name}に入ったにゃ！")

  def add_message_to_history(self, message, role="user"):
    author_id = message.author.id
    channel_id = message.channel.id
    content = message.content
    name = get_user_nickname(message.author)

    text = content

    if channel_id not in self.channel_message_history:
      self.channel_message_history[channel_id] = []

    # メッセージに添付ファイルがあるかチェック
    if message.attachments:
      for attachment in message.attachments:
        if 'image' in attachment.content_type:
          self.channel_message_history[channel_id].append({
            "role": role,
            "content": [
              {"type": "text", "text": f'{name}:{author_id} {text}'},
              {"type": "image_url", "image_url": {"url": attachment.url}}
            ]
          })

    if text == '':
      return False


    if role == "user":
      self.channel_message_history[channel_id].append({"role": "user", "content": f'{name}:{author_id} {text}'})
    elif role == "assistant":
      voice_state_update_pattern = re.compile(r'^.*が(.*)(からきえてくにゃ・・・|に入ったにゃ！)$')
      if voice_state_update_pattern.match(content):
        self.channel_message_history[channel_id].append({"role": "system", "content": f'{text}'})
      else:
        self.channel_message_history[channel_id].append({"role": "assistant", "content": f'{text}'})
    elif role == "system":
      self.channel_message_history[channel_id].append({"role": "system", "content": f'{text}'})

    # MAX_HISTORY_LENGTH件を超えた場合、最も古いメッセージを削除
    if len(self.channel_message_history[channel_id]) > self.MAX_HISTORY_LENGTH:
      self.channel_message_history[channel_id].pop(0)

    logger.info(self.channel_message_history)

    return True

  def get_reply(self, message, gpt_messages=None):
    if gpt_messages is None:
      gpt_messages = self.channel_message_history[message.channel.id]

    messages = send_prompt(gpt_messages, self.bot.user.id)

    return messages

  async def reply_to(self, message, gpt_messages=None):
    if gpt_messages is None:
      gpt_messages = self.channel_message_history[message.channel.id]

    async with message.channel.typing():
      messages = self.get_reply(message, gpt_messages)

    reply_message = await message.reply(messages[-1].content)

    await self.wait_reply(reply_message, messages)

  async def wait_reply(self, message, gpt_messages):
    def check(m):
      return m.reference is not None and m.reference.message_id == message.id

    msg = await self.bot.wait_for('message', timeout=180.0, check=check)
    gpt_messages.append({"role": "user", "content": f"{get_user_nickname(msg.author)}「{msg.content}」"})

    await self.reply_to(msg, gpt_messages)


async def setup(bot: commands.Bot):
  await bot.add_cog(EventsCog(bot))
