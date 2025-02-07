from django.db import models

class BotUser(models.Model):
    user_id = models.IntegerField(unique=True)  # Унікальний ідентифікатор користувача
    name = models.CharField(max_length=255)      # Ім'я користувача
    date_at = models.DateTimeField(auto_now_add=True)  # Дата створення запису

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE)  # Зовнішній ключ до моделі BotUser
    latitude = models.FloatField()  # Широта
    longitude = models.FloatField()  # Довгота
    subscribed_at = models.DateTimeField(auto_now_add=True)  # Дата підписки

    class Meta:
        indexes = [
            models.Index(fields=['user']),  # Індекс на зовнішній ключ
            models.Index(fields=['latitude', 'longitude']),  # Індекс на координати для швидшого пошуку
        ]

    def __str__(self):
        return f"Subscription for {self.user.name}"


class WeatherData(models.Model):
    city = models.CharField(max_length=255)  # Місто
    latitude = models.FloatField()  # Широта
    longitude = models.FloatField()  # Довгота
    description = models.CharField(max_length=255)  # Опис погоди
    temperature = models.FloatField()  # Температура
    humidity = models.FloatField()  # Вологість
    wind_speed = models.FloatField()  # Швидкість вітру
    temperature_unit = models.CharField(max_length=10, default='Celsius')  # Одиниці температури
    humidity_unit = models.CharField(max_length=10, default='%')  # Одиниці вологості
    wind_speed_unit = models.CharField(max_length=10, default='m/s')  # Одиниці швидкості вітру
    recorded_at = models.DateTimeField(auto_now_add=True)  # Дата запису

    def __str__(self):
        return f"Weather data for {self.city}"
