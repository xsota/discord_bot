# yukariちゃん

雑談してくれたり、誰かがボイスチャンネルに参加したことや、Cryptoの価格を教えてくれるDiscord botです

<img src="https://github.com/xsota/discord_bot/assets/5690642/bcf8670f-240a-4f2c-8ba2-aba5c02a6323" alt="かわいい顔の画像" width=320>

![image](https://github.com/xsota/discord_bot/assets/5690642/c43b10d7-5492-434a-83e9-710cb129f8ad)

![image](https://github.com/xsota/discord_bot/assets/5690642/4543f503-045a-46c8-9d69-1d5bf3bc557a)



## yukariちゃんとDiscordｎ招待したい人
yukariちゃんを[Discordに招待する](https://discordapp.com/api/oauth2/authorize?client_id=551785476584112139&permissions=0&scope=bot)


## ChatGPTを使ったDiscord botを自分の環境とかで動かしたい人
- git cloneする
- とりあえずbot.pyが動くように例えばpip installとかする
```
pip install -r src/requirements.txt
```
- .env.exampleを参考に環境変数を設定する (DiscordとかOpenAIのトークンとか、キャラのプロンプトとか)
- 動かしてみる
```
python src/bot.py
```

## とりあえずChatGPTを使ったおれおれDiscord botが欲しい人
- git cloneする
- fly.ioのアカウントを作ったりする
- flyctlをインストールしたりする (https://fly.io/docs/hands-on/install-flyctl/)
- プロンプトとか環境変数を.env.exampleを参考に設定する
```
fly deploy
```
