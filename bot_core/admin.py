from django.contrib import admin
from bot_user.models import BotUser


# Register your models here.
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'date_at', 'name']

admin.site.register(BotUser,UserInfoAdmin )