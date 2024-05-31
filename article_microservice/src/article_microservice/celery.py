from __future__ import absolute_import, unicode_literals
from datetime import timedelta
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'article_microservice.settings')

app = Celery('article_microservice')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'kafka-processing': {
        'task': 'apps.article.tasks.process_message',
        'schedule': timedelta(seconds=3),
    },
}
app.conf.timezone = 'UTC'
