from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('username', 'text', 'created_at')

admin.site.register(Message, MessageAdmin)
