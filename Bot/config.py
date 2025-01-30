from dotenv import load_dotenv
import os

# Завантажуємо .env
load_dotenv()

# Перевіряємо, чи файл .env існує і чи змінні завантажені
if not os.path.exists('.env'):
    raise FileNotFoundError("Файл .env не знайдений у проєкті.")

# Токени з .env файлу
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Перевіряємо наявність токенів
if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Помилка: не знайдено TELEGRAM_TOKEN або WEATHER_API_KEY у .env файлі")

print("Токени завантажено успішно!")
