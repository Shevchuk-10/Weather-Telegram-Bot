import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

WEATHER_API_KEY = "YOUR API KEY"
TELEGRAM_TOKEN = "YOUR TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привіт! Я бот погоди. Напишіть назву міста, щоб дізнатися погоду.")

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = update.message.text

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        await update.message.reply_text("Не вдалося отримати дані про погоду. Перевірте назву міста.")
        return

    city = data["name"]
    temperature = data["main"]["temp"]
    description = data["weather"][0]["description"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]

    weather_message = (
        f"Погода у {city}:\n"
        f"Температура: {temperature}°C\n"
        f"Відчувається як: {feels_like}°C\n"
        f"Опис: {description.capitalize()}\n"
        f"Вологість: {humidity}%"
    )

    await update.message.reply_text(weather_message)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))  

    application.run_polling()

if __name__ == "__main__":
    main()
