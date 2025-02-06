from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


# Налаштовуємо Django для роботи з Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djproject.settings')

# Створюємо об'єкт Celery
celery_app = Celery('djproject')

# Використовуємо конфігурації з Django для Celery
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Завантажуємо всі задачі з app/tasks.py
celery_app.autodiscover_tasks()

@celery_app.task(bind=True)
def debug_task(self):
    print('Debug task executed')
