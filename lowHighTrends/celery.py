from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from django.conf import settings
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lowHighTrends.settings')

app = Celery('lowHighTrends')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')
app.config_from_object(settings,namespace='CELERY')

#celery beat settings
app.conf.beat_schedule = {
    'test-run':{
        'task': 'App.tasks.scheduled_task',
        # 'schedule': crontab(hour='9',minute='10',day_of_week='mon,tue,wed,thu,fri')
        'schedule': crontab(hour='9',minute='15',day_of_week='1-5'),
        # 'args':"TEST ARGUMENT, IT IS WORKING WOW"
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request:{self.request!r}')