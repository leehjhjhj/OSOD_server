# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from .email import SubMailView
from django.test import RequestFactory
from django.http import HttpRequest
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
        self.cnt = 0
        self.scheduler = BackgroundScheduler()
        self.is_running = False  # 스케줄러 실행 여부
        self.job_id = 'my_job_id'
        self.scheduler.add_job(
            self.my_job,
            'cron',
            day_of_week='*',
            hour=9,
            minute=29,
            second=00,
            id=self.job_id
        )

        self.sub_mail_view = SubMailView()

    def my_job(self):
        if self.is_running:  # 이미 실행중인 경우
            return
    
        try:
            self.is_running = True  # 스케줄러 실행 중으로 변경
            # request = HttpRequest()
            # self.sub_mail_view.get(request)
            self.sub_mail_view.get(request=None)
            self.cnt += 1
            print(self.cnt)
            if self.cnt == 1:
                return
        except Exception as e:
            print(e)
        finally:
            self.is_running = False  # 스케줄러 실행 종료로 변경
            self.scheduler.remove_job(self.job_id)
