from rest_framework import serializers

from bot_user.models import BotUser


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = ['user_id','name']