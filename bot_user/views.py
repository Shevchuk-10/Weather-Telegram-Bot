import logging
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

        if not all([user_id, latitude, longitude]):
            logger.error(f"Помилка: відсутні дані (user_id={user_id}, latitude={latitude}, longitude={longitude})")
            return Response({"error": "Missing data (user_id, latitude, longitude)"},
                            status=status.HTTP_400_BAD_REQUEST)

        user, created = BotUser.objects.get_or_create(user_id=user_id)
        subscription, created = Subscription.objects.get_or_create(user=user, latitude=latitude, longitude=longitude)

        logger.info(f"Підписка створена: {subscription}")

        return Response({"message": "Successfully subscribed!"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Помилка під час обробки: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # Перевірка, чи існує користувач з таким user_id
        user = BotUser.objects.filter(user_id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Створення підписки
        subscription = Subscription.objects.create(user=user, latitude=latitude, longitude=longitude)

        # Повідомлення про успішну підписку
        return Response({"message": "Successfully subscribed!"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Помилка під час обробки: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        # Створення підписки
        subscription = Subscription.objects.create(user=user, latitude=latitude, longitude=longitude)
        logger.info(f"Успішно створено підписку для користувача {user.name}")

        # Повідомлення про успішну підписку
        return Response({"message": "Successfully subscribed!"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Помилка під час обробки: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # Перевірка, чи існує користувач з таким user_id
        user = BotUser.objects.filter(user_id=user_id).first()
        if not user:
            logger.error(f"Користувач з user_id={user_id} не знайдений")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Створення підписки
        subscription = Subscription.objects.create(user=user, latitude=latitude, longitude=longitude)
        logger.info(f"Успішно створено підписку для користувача {user.name}")

        # Повідомлення про успішну підписку
        return Response({"message": "Successfully subscribed!"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Помилка під час обробки: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_subscribers(request):
    """Отримання всіх підписників"""
    subscribers = BotUser.objects.all()
    serializer = BotUserSerializer(subscribers, many=True)
    logger.info(f"Кількість підписників: {len(subscribers)}")
    return Response(serializer.data)


@api_view(['POST'])
def send_weather_update(request):
    """Відправка оновлення погоди всім підписникам"""
    logger.info("Відправка оновлень погоди всім підписникам")
    # Тут може бути код для відправки оновлень всім підписникам, використовуючи Telegram API.
    return Response({"message": "Weather updates sent!"})
