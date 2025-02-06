import os
import json
import logging
import aiohttp
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv



# Загружаем переменные окружения
load_dotenv()

# Переменные окружения
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DJANGO_API_URL = "http://127.0.0.1:8000/api/subscribe/"

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_weather_data(url: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except Exception as e:
        logger.error(f"Ошибка при запросе данных о погоде: {e}")
        return {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("📍 Отправить геолокацию", request_location=True)],
        [KeyboardButton("✍ Ввести город вручную")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Привет! Я бот погоды. Выберите, как хотите получить погоду:",
                                    reply_markup=reply_markup)


async def get_weather_by_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    user_id = update.message.chat_id

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    data = await fetch_weather_data(url)

    if not data or data.get("cod") != 200:
        await update.message.reply_text("❌ Не удалось получить погоду для вашей геолокации. Попробуйте снова.")
        return

    weather_message = format_weather_message(data)

    keyboard = [[InlineKeyboardButton("🔔 Подписаться на уведомления",
                                      callback_data=f"subscribe_location_{latitude}_{longitude}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(weather_message, reply_markup=reply_markup)


async def get_weather_by_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city_name = update.message.text.strip()
    if city_name.lower() in ["ввести город вручную", "✍ ввести город вручную"]:
        await update.message.reply_text("✍ Пожалуйста, введите название города вручную:")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    data = await fetch_weather_data(url)

    if not data or data.get("cod") != 200:
        await update.message.reply_text("❌ Не удалось найти погоду для указанного города. Попробуйте снова.")
        return

    weather_message = format_weather_message(data)
    keyboard = [[InlineKeyboardButton("🔔 Подписаться на уведомления", callback_data=f"subscribe_city_{city_name}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(weather_message, reply_markup=reply_markup)


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    user_id = query.message.chat.id

    if data[1] == "city":
        city_name = "_".join(data[2:])
        payload = {"user_id": user_id, "city": city_name}
    else:
        latitude, longitude = data[2], data[3]
        payload = {"user_id": user_id, "latitude": latitude, "longitude": longitude}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DJANGO_API_URL, json=payload) as response:
                response.raise_for_status()
        await query.edit_message_text("✅ Вы подписались на уведомление о погоде!")
    except Exception as e:
        await query.edit_message_text("❌ Ошибка при подписке. Попробуйте позже.")
        logger.error(f"Ошибка при подписке: {e}")


def format_weather_message(data: dict) -> str:
    city_name = data.get("name", "Неизвестное место")
    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    return (
        f"🌍 Погода в {city_name}:\n"
        f"🌡 Температура: {temperature}°C\n"
        f"🤔 Ощущается как: {feels_like}°C\n"
        f"📜 Описание: {description.capitalize()}\n"
        f"💧 Влажность: {humidity}%\n"
        f"💨 Скорость ветра: {wind_speed} м/с"
    )


def run_telegram_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, get_weather_by_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather_by_city))
    app.add_handler(CallbackQueryHandler(subscribe))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    run_telegram_bot()
