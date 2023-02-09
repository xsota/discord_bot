import os
import openai

def send_prompt(prompt=''):
  openai.api_key = os.environ.get('OPEN_AI_API_KEY')

  start_sequence = "\nAI:"
  restart_sequence = "\nHuman: "

  response = openai.Completion.create(
    model= 'text-davinci-003',
    #model= 'text-ada-001',
    prompt="Below is the conversation with the Japanese girl AI yukari. The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\nAI: Hi, I am  yukari\nHuman: "+prompt+"\nAI:",
    temperature=0.9,
    max_tokens=200,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.5,
    stop=[" Human=", " AI="]
  )

  print(response)

  return response['choices'][0]['text']

