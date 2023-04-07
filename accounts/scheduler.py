# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from .email import SubMailView
from django.test import RequestFactory
# class MyScheduler:
#     def __init__(self):
#         self.scheduler = BackgroundScheduler()
#         self.scheduler.add_job(self.my_job, 'cron', day_of_week='*', hour=23, minute=36, second=40)

#     def my_job(self):
#         # view = SubMailView()
#         # view.get(request=None)
#         request = RequestFactory().get('/')
#         SubMailView.as_view()(request)
class MyScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.my_job,
            'cron',
            day_of_week='*',
            hour=23,
            minute=45,
            second=00,
            id='my_job_id'
        )

    def my_job(self):
        try:
            # view = SubMailView()
            # view.get(request=None)
            request = RequestFactory().get('/')
            SubMailView.as_view()(request)
        except Exception as e:
            # 예외 처리
            print(e)
        finally:
            self.scheduler.remove_job('my_job_id')