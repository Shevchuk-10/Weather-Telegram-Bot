import os
import aiohttp
import logging
from datetime import datetime, timedelta
from django.conf import settings


logger = logging.getLogger(__name__)

# Ваш API ключ OpenWeather
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") # Додайте свій ключ API в settings.py

# Функція для отримання прогнозу погоди
async def fetch_weather_data(lat: float, lon: float) -> dict:
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except Exception as e:
        logger.error(f"Помилка при запиті погодних даних: {e}")
        return {}

# Функція для перевірки дощу
async def check_rain(weather_data: dict):
    for forecast in weather_data['list']:
        dt = datetime.utcfromtimestamp(forecast['dt'])
        rain = forecast.get('rain', {}).get('3h', 0)

        if rain > 0:  # Якщо є дощ
            rain_start_time = dt - timedelta(minutes=20)
            return rain_start_time, True
    return None, False
