import base64
import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import json
load_dotenv()

account_key_json = base64.b64decode(os.environ.get('FIREBASE_SERVICE_ACCOUNT_BASE64')).decode()
cred = credentials.Certificate(json.loads(account_key_json))
firebase_admin.initialize_app(cred)



import requests

project_id = 'your_firebase_project_id'
url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{project_id}/remoteConfig"

headers = {
  'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
  remote_config_data = response.json()
  # 必要なパラメータを取得
  parameter_value = remote_config_data['parameters']['your_parameter_key']['defaultValue']['value']
  print(parameter_value)
else:
  print(f"Error: {response.status_code}, {response.text}")
