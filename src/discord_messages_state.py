from langgraph.graph import MessagesState


class DiscordMessagesState(MessagesState):
  current_channel_id: int  # チャンネルIDを追加
