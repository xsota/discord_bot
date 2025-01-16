import os
from typing import Literal
from dotenv import load_dotenv

load_dotenv()
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from meowgent import Meowgent

character_prompt = os.environ.get('CHARACTER_PROMPT')

# エージェントが使用するツールを定義
@tool
def search(query: str):
  """Web検索を行うツール"""
  print(f"[search] ツールが呼び出されました。クエリ: {query}")

  return "最高のそばはアルティメットそーばと言われていますが"

tools = [search]

# モデルを初期化
model = ChatOpenAI(
  model=os.environ.get('OPEN_AI_MODEL'),
  openai_api_key=os.environ.get('OPEN_AI_API_KEY'),
  openai_api_base=os.environ.get('OPEN_AI_API_URL'),
  max_tokens=int(os.environ.get('OPEN_AI_MAX_TOKEN')),
  temperature=float(os.environ.get('TEMPERATURE', 1))
)
print("[INFO] モデルが初期化され、ツールがバインドされました。")


# 状態を永続化するためのメモリを初期化
checkpointer = MemorySaver()
print("[INFO] メモリセーバーが初期化されました。")

meowgent = Meowgent(
  model=model,
  tools=tools,
  system_prompt=character_prompt,
  checkpointer=checkpointer,
)

# Runnableを使用
print("[INFO] グラフの実行を開始します。")
final_state = meowgent.app.invoke(
  {"messages": [HumanMessage(content="最高のそばを教えて")]},
  config={"configurable": {"thread_id": 42, "recursion_limit": 5}}
)
print("[INFO] グラフの実行が完了しました。")

# 最後のメッセージ内容を出力
print(f"[RESULT] 最後の応答内容: {final_state['messages'][-1].content}")
