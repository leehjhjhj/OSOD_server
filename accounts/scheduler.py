from apscheduler.schedulers.background import BackgroundScheduler
from django.db import close_old_connections
from .email import SubMailView
class MyScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(max_instances=1)
        self.job_id = 'my_job_id'
        self.sub_mail_view = SubMailView()
        self.scheduler.add_job(
            self.my_job,
            'cron',
            day_of_week='*',
            hour=6,
            minute=30,
            second=00,
            id=self.job_id
        )

    def my_job(self):
        try:
            close_old_connections()
            print('SubMailView.get() function is called.')
            self.sub_mail_view.get(request=None)
        except Exception as e:
            print(e)

        



