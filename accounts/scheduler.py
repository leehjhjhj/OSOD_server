# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from .email import SubMailView
class MyScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.my_job, 'cron', day_of_week='*', hour=23, minute=32, second=00)

    def my_job(self):
        view = SubMailView()
        view.get(request=None)
        
