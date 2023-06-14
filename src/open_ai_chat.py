import os
from datetime import datetime

import openai

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

def send_prompt(messages):
  if any(item.get("role") != "system" for item in messages):
    messages = [{"role": "system", "content": os.environ.get('CHARACTER_PROMPT')},
                {"role": "system", "content": "User comments are in the format Name: Comment"},
                {"role": "system", "content": f"Current JST:{formatted_datetime}"},
                {"role": "user", "content": "name: hi!"},
                {"role": "assistant", "content": "こんにちは！"}
                ] + messages

  openai.api_key = os.environ.get('OPEN_AI_API_KEY')

  try:
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0613",
      # model="gpt-3.5-turbo",
      # model="gpt-4",
      messages=messages,
      timeout=10
    )

    messages.append(response['choices'][0]['message'])

    return messages
  except:
    raise
