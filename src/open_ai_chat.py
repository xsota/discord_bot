import os
import openai
import requests
import json

def send_prompt(prompt=''):
  openai.api_key = os.environ.get('OPEN_AI_API_KEY')

  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role":"system", "content": "Below is a conversation with the AI assistant. The AI assistant's name is Yukari and she is a Japanese girl. The age of the AI assistant is 16 years old. AI assistants think of themselves as people, not AIs."},
      {"role":"user", "content": prompt}
    ]
  )

  print(response)

  return response['choices'][0]['message']['content']
