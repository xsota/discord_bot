from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from logging import getLogger
logger = getLogger(__name__)

class Meowgent:
  def __init__(self, model, tools, system_prompt, checkpointer=None):
    self.system_prompt = system_prompt
    self.model = model
    self.tools = tools
    self.checkpointer = checkpointer

    # 新しいグラフを定義
    workflow = StateGraph(MessagesState)
    logger.info("The graph has been initialized.")
    workflow.add_node("agent", self.call_model)

    # ツールの設定
    self.tools = {t.name: t for t in tools}
    self.model = model.bind_tools(tools)

    tool_node = ToolNode(tools)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
      "agent",
      self.should_continue,
    )
    logger.info("Conditional edges have been added to 'agent'.")

    # toolのあとはagent
    workflow.add_edge("tools", 'agent')

    self.app = workflow.compile(checkpointer=checkpointer)
    logger.info("The graph has been compiled.")


  # 処理を継続するかどうかを決定する
  def should_continue(self, state: MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    logger.info(f"[should_continue] The last message: {last_message.content}")
    if last_message.tool_calls:
      logger.info("[should_continue] A tool call has been detected. Next node: tools")
      return "tools"
    logger.info("[should_continue] No tool call detected. Next node: END")
    return END

  # モデルを呼び出す関数
  def call_model(self, state: MessagesState):
    system_message = SystemMessage(content=self.system_prompt)

    messages = [system_message] + state['messages']
    logger.info(f"[call_model] Messages passed to the model: {[msg.content for msg in messages]}")
    response = self.model.invoke(messages)
    logger.info(f"[call_model] Response from the model: {response}")

    return {"messages": [response]}
