from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from bot_user.task import check_rain_for_subscribed_users  # правильний імпорт функції


class BotUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot_user'

    def ready(self):
        scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
        scheduler.add_job(check_rain_for_subscribed_users, 'interval', minutes=10)  # Перевірка кожні 10 хвилин
        scheduler.start()

