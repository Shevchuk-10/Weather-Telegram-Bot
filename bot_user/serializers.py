from rest_framework import serializers
from .models import BotUser, Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'latitude', 'longitude', 'subscribed_at']

class BotUserSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionSerializer(many=True, read_only=True)  # Додаємо підписки користувача

    class Meta:
        model = BotUser
        fields = ['id', 'user_id', 'name', 'date_at', 'subscriptions']
