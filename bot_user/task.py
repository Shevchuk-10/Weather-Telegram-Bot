import os
import requests
from datetime import datetime, timedelta
from Bot import bot
from bot_user.models import Subscription



def check_rain_for_subscribed_users():
    # Витягуємо всі підписки з бази даних
    subscriptions = Subscription.objects.all()

    for subscription in subscriptions:
        # Отримуємо прогноз погоди для координат підписки
        url = f"http://api.openweathermap.org/data/2.5/onecall?lat={subscription.latitude}&lon={subscription.longitude}&exclude=current,minutely,hourly&appid={os.getenv('WEATHER_API_KEY')}&units=metric&lang=ru"
        response = requests.get(url)

        if response.status_code == 200:
            forecast = response.json()
            # Перевіряємо прогноз на дощ за наступні 20 хвилин
            for hourly_data in forecast["hourly"]:
                dt = datetime.utcfromtimestamp(hourly_data["dt"])  # Час прогнозу
                if dt <= datetime.utcnow() + timedelta(minutes=20):  # Якщо прогноз на найближчі 20 хвилин
                    if "rain" in hourly_data:
                        rain_start = dt
                        message = f"⛈ Важливо: дощ очікується через 20 хвилин! Час початку: {rain_start.strftime('%H:%M:%S')}"
                        send_weather_alert(subscription.user, message)
                        break


def send_weather_alert(user, message):
    # Відправляємо повідомлення користувачу
    bot.send_message(user.telegram_chat_id, message)
