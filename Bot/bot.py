import os
import logging
import aiohttp
import requests
from telegram.ext import CallbackQueryHandler
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Отримуємо ключ API та токен Telegram
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Налаштовуємо логування
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


# Функція для отримання даних про погоду
async def fetch_weather_data(url: str) -> dict:
    """Получение данных о погоде"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


# Обробник команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    responce = requests.post('http://127.0.0.1:8000/user_management/user_info/',
                             json={
                                 'user_id': update.message.chat_id,
                                 'name': f'{update.message.chat.first_name} {update.message.chat.last_name}'
                             })
    keyboard = [
        [KeyboardButton("Отправить свою геолокацию", request_location=True)],
        [KeyboardButton("Написать место вручную")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот погоды. Выберите, как хотите получить погоду:",
        reply_markup=reply_markup
    )


# Обробник введення міста вручну
async def get_weather_by_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получение погоды по введенному городу"""
    city_name = update.message.text.strip()

    if not city_name:
        await update.message.reply_text('Пожалуйста, введите название города.')
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    try:
        data = await fetch_weather_data(url)
        if data.get('cod') != 200:
            await update.message.reply_text(
                'Напишите место чтобы узнать погоду.')
            return

        city_name = data.get("name", "неизвестное место")
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_message = (
            f"🌍 Погода в {city_name}:\n"
            f"🌡 Температура: {temperature}°C\n"
            f"🤔 Ощущается как: {feels_like}°C\n"
            f"📜 Описание: {description.capitalize()}\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Скорость ветра: {wind_speed} м/с"
        )

        # Кнопка "Подписаться"
        keyboard = [[InlineKeyboardButton("🔔 Подписаться", callback_data=f"subscribe_{city_name}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(weather_message, reply_markup=reply_markup)

    except aiohttp.ClientError as req_e:
        await update.message.reply_text("Ошибка при получении данных о погоде. Попробуйте еще раз.")
        logger.error(f"Ошибка запроса погоды для города {city_name}: {req_e}")
    except Exception as ex:
        await update.message.reply_text(f"Произошла непредвиденная ошибка: {ex}")
        logger.error(f"Неожиданная ошибка: {ex}")


# Обробник отримання погоди за геолокацією
async def get_weather_by_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получение погоды по геолокации пользователя"""
    location = update.message.location

    if not location:
        await update.message.reply_text("Не удалось получить вашу геолокацию.")
        return

    lat, lon = location.latitude, location.longitude
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    try:
        data = await fetch_weather_data(url)
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
            f"🌍 Погода в {city_name}:\n"
            f"🌡 Температура: {temperature}°C\n"
            f"🤔 Ощущается как: {feels_like}°C\n"
            f"📜 Описание: {description.capitalize()}\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Скорость ветра: {wind_speed} м/с"
        )

        # Кнопка "Подписаться"
        keyboard = [[InlineKeyboardButton("🔔 Подписаться", callback_data=f"subscribe_{lat}_{lon}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(weather_message, reply_markup=reply_markup)

    except aiohttp.ClientError as req_e:
        await update.message.reply_text("Ошибка при получении данных о погоде. Попробуйте еще раз.")
        logger.error(f"Ошибка запроса погоды {lat}, {lon}: {req_e}")
    except Exception as ex:
        await update.message.reply_text(f"Произошла непредвиденная ошибка: {ex}")
        logger.error(f"Неожиданная ошибка: {ex}")


# Обробник підписки на сповіщення про погоду
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик подписки на уведомления о погоде"""
    query = update.callback_query
    await query.answer()

    # Получаем координаты из callback_data
    _, lat, lon = query.data.split("_")
    user_id = query.message.chat_id

    # Отправляем данные в бэкенд (тут тебе нужно сделать API для подписки)
    response = requests.post("http://127.0.0.1:8000/weather/subscribe/", json={
        "user_id": user_id,
        "latitude": lat,
        "longitude": lon
    })

    if response.status_code == 200:
        await query.edit_message_text("✅ Вы подписались на уведомления о погоде!")
    else:
        await query.edit_message_text("❌ Ошибка при подписке. Попробуйте позже.")


# Функція для запуску бота
def run_telegram_bot():
    """Запуск Telegram-бота"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN не найден. Проверьте .env файл!")
        return

    # Ініціалізуємо додаток для бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додаємо обробники команд та повідомлень
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.LOCATION, get_weather_by_location))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather_by_city))

    logger.info("Бот запущен...")
    application.run_polling()


# Точка входу для запуску бота
if __name__ == "__main__":
    run_telegram_bot()
