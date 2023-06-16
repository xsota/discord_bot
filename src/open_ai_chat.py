import os
from datetime import datetime

import openai
import json

from igdb import search_games_by_theme_ids, get_themes

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

# botに使ってほしいfunction
functions = [
  {
    "name": "search_games_by_theme_ids",
    "description": "Search popular games by theme ID, ID: 20 - Thriller, ID: 18 - Science fiction, ID: 1 - Action, ID: 19 - Horror, ID: 21 - Survival, ID: 17 - Fantasy, ID: 22 - Historical, ID: 23 - Stealth, ID: 27 - Comedy, ID: 28 - Business, ID: 31 - Drama, ID: 32 - Non-fiction, ID: 35 - Kids, ID: 33 - Sandbox, ID: 38 - Open world, ID: 39 - Warfare, ID: 41 - 4X (explore, expand, exploit, and exterminate), ID: 34 - Educational, ID: 43 - Mystery, ID: 40 - Party, ID: 44 - Romance, ID: 42 - Erotic",
    "parameters": {
      "type": "object",
      "properties": {
        "theme_ids": {
          "type": "array",
          "items": {
            "type": "integer"
          },
          "description": "theme_id list",
        },
      },
      "required": ["theme_ids"],
    },
  },
  # {
  #   "name": "get_themes",
  #   "description": "Get IDs to use for search_games_by_theme_ids",
  #   "parameters": {"type": "object", "properties": {}}
  # },
]


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
      # model="gpt-4-0613",
      messages=messages,
      functions=functions,
      function_call="auto",
      timeout=10
    )

    message = response['choices'][0]['message']
    messages.append(message)

    # modelがfunctionの呼び出しを求めている
    if message.get("function_call"):
      function_name = message["function_call"]["name"]

      # modelの求めるfunctionを呼ぶ
      match function_name:
        case "get_themes":
          print(message)
          function_response = str(get_themes())
          print(function_response)
        case "search_games_by_theme_ids":
          print(message)
          function_response = str(search_games_by_theme_ids(
            theme_ids=message.get("theme_ids"),
          ))
          print(function_response)

      # modelに結果を送る
      second_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages + [{
          "role": "function",
          "name": function_name,
          "content": function_response,
        }]
      )
      message = second_response['choices'][0]['message']
      messages.append(message)

    print(messages)
    return messages
  except:
    raise
