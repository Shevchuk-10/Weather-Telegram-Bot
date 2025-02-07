import logging
import os
import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import BotUser, Subscription
from .serializers import BotUserSerializer, SubscriptionSerializer



logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
def subscribe(request):
    logger.info(f"Запит отримано: {request.data}")  # Лог вхідних даних

    try:
        user_id = request.data.get('user_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        logger.info(f"user_id={user_id}, latitude={latitude}, longitude={longitude}")  # Лог параметрів

        # Перевірка на наявність даних для координат
        if not user_id or not latitude or not longitude:
            logger.error(f"Помилка: відсутні дані (user_id={user_id}, latitude={latitude}, longitude={longitude})")
            return Response({"error": "Missing data (user_id, latitude, longitude)"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Перевірка на типи для координат
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            logger.error(f"Помилка: невірний формат координат (latitude={latitude}, longitude={longitude})")
            return Response({"error": "Invalid coordinates format"}, status=status.HTTP_400_BAD_REQUEST)

        # Створюємо або знаходимо користувача
        user, created = BotUser.objects.get_or_create(user_id=user_id)

        # Створюємо або знаходимо підписку
        subscription, created = Subscription.objects.get_or_create(user=user, latitude=latitude, longitude=longitude)

        if created:
            logger.info(f"Підписка успішно створена для користувача {user_id} з геолокацією ({latitude}, {longitude})")
            return Response({"message": "Successfully subscribed!"}, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"Підписка вже існує для користувача {user_id}")
            return Response({"message": "Already subscribed!"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Помилка під час обробки: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_message(user_id: int, message: str):
    url = f"https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка при відправці повідомлення через Telegram API: {e}")

@api_view(['GET'])
def get_subscribers(request):
    try:
        # Отримуємо всі підписки з бази даних
        subscriptions = Subscription.objects.all()

        # Серіалізуємо список підписок
        serializer = SubscriptionSerializer(subscriptions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Помилка при отриманні підписників: {e}")
        return Response({"error": "Не вдалося отримати підписників"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)