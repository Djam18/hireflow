import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hireflow.settings')

# Celery 5.0: app instantiation unchanged but CLI is now `celery -A hireflow worker`
# (removed deprecated `celery worker -A hireflow` form)
app = Celery('hireflow')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def debug_task(self):
    """Celery 5.0: bind=True gives access to self for retry logic."""
    print(f'Request: {self.request!r}')
