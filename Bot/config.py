from dotenv import load_dotenv
import os

# Завантажуємо .env
load_dotenv()

# Перевіряємо, чи токени завантажилися
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Помилка: не знайдено TELEGRAM_TOKEN або WEATHER_API_KEY у .env файлі")