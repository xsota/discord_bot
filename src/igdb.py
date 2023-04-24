import os
import time
import requests

from dotenv import load_dotenv

load_dotenv()

# 環境変数からTwitch APIのClient IDとClient Secretを取得
CLIENT_ID = os.environ.get('TWITCH_API_CLIENT_ID')
CLIENT_SECRET = os.environ.get('TWITCH_API_CLIENT_SECRET')


# アクセストークンクラス
class AccessToken:
  def __init__(self, token, expires_in):
    self.token = token

    # 無効になる60秒前に更新するようにマージンを設ける
    self.expires_at = time.time() + expires_in - 60

  # アクセストークンが期限切れかどうかを判断
  def is_expired(self):
    return time.time() > self.expires_at


# IGDB APIのアクセストークンを取得する関数
def get_igdb_access_token(client_id, client_secret):
  url = "https://id.twitch.tv/oauth2/token"
  payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
  }
  response = requests.post(url, params=payload)
  data = response.json()
  access_token = data["access_token"]
  expires_in = data["expires_in"]
  return AccessToken(access_token, expires_in)


# アクセストークンオブジェクトを初期化
access_token_obj = get_igdb_access_token(CLIENT_ID, CLIENT_SECRET)


# アクセストークンを取得または更新する関数
def get_access_token():
  # トークンが期限切れの場合、新しいトークンを取得
  if access_token_obj.is_expired():
    new_token_obj = get_igdb_access_token(CLIENT_ID, CLIENT_SECRET)
    access_token_obj.token = new_token_obj.token
    access_token_obj.expires_at = new_token_obj.expires_at
  return access_token_obj.token


# IGDB APIからテーマの一覧を取得する関数
def get_themes():
  url = "https://api.igdb.com/v4/themes"
  headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {get_access_token()}",
    "Accept": "application/json"
  }
  payload = "fields name; limit 500;"

  response = requests.post(url, data=payload, headers=headers)
  data = response.json()

  return data


# 複数のテーマIDを使用してIGDB APIからゲームを検索する関数
def search_games_by_theme_ids(theme_ids):
  url = "https://api.igdb.com/v4/games"
  headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {get_access_token()}",
    "Accept": "application/json"
  }

  # リスト内の数値だけをカンマ区切りの文字列に変換
  numeric_theme_ids = [str(x) for x in theme_ids if isinstance(x, (int, float))]
  theme_ids_str = ','.join(numeric_theme_ids)

  payload = f"""
    fields name, themes;
    where themes = [{theme_ids_str}] & total_rating_count > 1;
    sort total_rating desc;
    limit 10;
    """

  response = requests.post(url, data=payload, headers=headers)
  data = response.json()
  if not data:
    print(f"テーマID {theme_ids} に一致するゲームが見つかりませんでした。")
    return []

  return data
