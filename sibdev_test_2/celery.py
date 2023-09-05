import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sibdev_test_2.settings')
app = Celery('sibdev_test_2')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(name='debug_task')
def debug_task(*args, **kwargs):
    """
    Отладочная задача Celery, печатает и возвращает строковое представление
    собственного вызова.
    """
    args = ', '.join(map(repr, args))
    kwargs = ', '.join('{}={}'.format(k, repr(v)) for k, v in kwargs.items())
    total = filter(None, (args, kwargs))
    representation = 'debug_task {}'.format(', '.join(total))
    print(representation)
    return representation
