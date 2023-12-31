import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sibdev_test_2.settings')
app = Celery('sibdev_test_2')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
