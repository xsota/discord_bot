import asyncio
from logging import getLogger

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = getLogger(__name__)

class TaskManager:
  def __init__(self, db_url='sqlite:///jobs.sqlite', timezone='Asia/Tokyo'):
    self.timezone = pytz.timezone(timezone)
    self.scheduler = AsyncIOScheduler(jobstores={
      # 'default': SQLAlchemyJobStore(url=db_url),
    }, event_loop=asyncio.get_event_loop())

  def start_scheduler(self):
    """スケジューラを起動"""
    self.scheduler.start()
    logger.info("Scheduler has started!")

  def add_task(self, func, run_date, args=None, task_id=None):
    """タスクを追加"""
    run_date = self.timezone.localize(run_date)
    self.scheduler.add_job(func, 'date', run_date=run_date, args=args or [], id=task_id)
    logger.info(f"Task has been added: {task_id}")

