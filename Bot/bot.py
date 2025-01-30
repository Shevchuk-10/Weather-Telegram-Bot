import os
import requests
from dotenv import load_dotenv
from telegram import Update
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник команди /start"""
    await update.message.reply_text("Привіт! Я бот погоди. Напишіть назву міста, щоб дізнатися погоду.")


async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник текстових повідомлень (отримання погоди)"""
    city = update.message.text.strip()

    if not city:
        await update.message.reply_text("Будь ласка, введіть назву міста.")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("cod") != 200:
            await update.message.reply_text("Не вдалося знайти місто. Перевірте правильність написання.")
            return

        # Отримання даних про погоду
        city_name = data["name"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        # Формування повідомлення
        weather_message = (
            f"🌤 Погода у {city_name}:\n"
            f"🌡 Температура: {temperature}°C\n"
            f"🤔 Відчувається як: {feels_like}°C\n"
            f"📜 Опис: {description.capitalize()}\n"
            f"💧 Вологість: {humidity}%"
        )

        await update.message.reply_text(weather_message)

    except requests.exceptions.RequestException:
        await update.message.reply_text("Помилка при отриманні даних про погоду. Спробуйте ще раз.")
    except Exception as e:
        await update.message.reply_text(f"Сталася непередбачена помилка: {e}")


def main():
    """Запуск Telegram-бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))

    print("✅ Бот запущений...")
    application.run_polling()


# Перевіряємо, чи цей файл запущений напряму
if __name__ == "__main__":
    main()
