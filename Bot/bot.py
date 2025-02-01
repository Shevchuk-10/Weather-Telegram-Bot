import os
import requests
import logging
import aiohttp
from dotenv import load_dotenv
from telegram import Update
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Завантажуємо змінні з .env
load_dotenv()

# Токени (з .env файлу)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Перевірка на наявність необхідних змінних середовища
if not WEATHER_API_KEY or not TELEGRAM_TOKEN:
    print("❌ Помилка: не знайдені змінні WEATHER_API_KEY або TELEGRAM_TOKEN")
    exit(1)

# Налаштування логування
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_weather_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник команди /start"""
    keyboard = [
        [KeyboardButton("Отправить свою геолокацию", request_location=True)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот погоды. Отправьте свою геолокацию для получения погоды или напишите название города:",
        reply_markup=reply_markup
    )

async def get_weather_by_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отримання погоди за геолокацією користувача"""
    location = update.message.location

    if not location:
        await update.message.reply_text("Не удалось получить вашу геолокацию.")
        return

    lat, lon = location.latitude, location.longitude
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ua"

    try:
        data = await fetch_weather_data(url)  # Використовуємо асинхронну функцію
        if data.get("cod") != 200:
            await update.message.reply_text("Не удалось найти погоду для этой локации.")
            return

        city_name = data.get("name", "неизвестное место")
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_message = (
            f"🌍 Погода у {city_name}:\n"
            f"🌡 Температура: {temperature}°C\n"
            f"🤔 Чувствуется как: {feels_like}°C\n"
            f"📜 Описание: {description.capitalize()}\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Скорость ветра: {wind_speed} м/с"
        )

        await update.message.reply_text(weather_message)

    except aiohttp.ClientError as req_e:
        await update.message.reply_text("Ошибка при получении данных о погоде. Попытайтесь еще раз.")
        logger.error(f"Error fetching weather data for location {lat}, {lon}: {req_e}")
    except Exception as ex:
        await update.message.reply_text(f"Произошла непредвиденная ошибка:: {ex}")
        logger.error(f"Unexpected error: {ex}")



async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник текстових повідомлень (отримання погоди по назві міста)"""
    city = update.message.text.strip()

    if not city:
        await update.message.reply_text("Введите название города.")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua"

    try:
        data = await fetch_weather_data(url)  # Використовуємо асинхронну функцію

        if data.get("cod") != 200:
            await update.message.reply_text("Не удалось найти город. Проверьте правильность написания.")
            return

        # Отримання даних про погоду
        city_name = data["name"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        # Формування повідомлення
        weather_message = (
            f"🌤 Погода у {city_name}:\n"
            f"🌡 Температура: {temperature}°C\n"
            f"🤔 Чувствуется как: {feels_like}°C\n"
            f"📜 Описание: {description.capitalize()}\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Скорость ветра: {wind_speed} м/с"
        )

        await update.message.reply_text(weather_message)

    except aiohttp.ClientError as req_e:
        await update.message.reply_text("Ошибка при получении данных о погоде. Попробуйте еще раз.")
        logger.error(f"Error fetching weather data for {city}: {req_e}")
    except Exception as ex:
        await update.message.reply_text(f"Произошла непредвиденная ошибка: {ex}")
        logger.error(f"Unexpected error: {ex}")


def main():
    """Запуск Telegram-бота"""
    global application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))

    # Добавляем обработчик геолокации
    application.add_handler(MessageHandler(filters.LOCATION, get_weather_by_location))

    # Запуск бота
    application.run_polling()


# Перевіряємо, чи цей файл запущений напряму
if __name__ == "__main__":
    main()
