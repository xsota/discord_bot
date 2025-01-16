import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
import pytz

# タイムゾーン設定
TIMEZONE = pytz.timezone("Asia/Tokyo")

# SQLiteを使ったJobStoreの設定
jobstores = {
  'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

# APSchedulerのスケジューラ設定
scheduler = AsyncIOScheduler(jobstores=jobstores)

# タスクをスケジュールする関数
def my_task(message):
  print(f"タスク実行中: {message} ({datetime.now()})")

# メイン関数
async def main():
  # スケジューラの起動
  scheduler.start()

  # タスクの追加
  task_time = TIMEZONE.localize(datetime(2025, 1, 15, 14, 47))
  scheduler.add_job(my_task, 'date', run_date=task_time, args=["こんにちは！"], id="task2")

  print("スケジューラ起動中...")

  # イベントループを動かし続ける
  while True:
    await asyncio.sleep(1)

# asyncioのイベントループを起動
if __name__ == "__main__":
  asyncio.run(main())
