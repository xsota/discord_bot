import os
import openai
import requests
import json

def send_prompt(prompt='', messages=None):
  if messages is None:
    messages = [{"role": "system",
               "content": "Below is a conversation with the AI assistant. The AI assistant's name is Yukari and she is a Japanese girl. The age of the AI assistant is 16 years old. AI assistants think of themselves as people, not AIs."}]

  openai.api_key = os.environ.get('OPEN_AI_API_KEY')

  messages.append({"role":"user", "content": prompt})

  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
  )

  print(response)

  messages.append(response['choices'][0]['message'])

  return response['choices'][0]['message']
