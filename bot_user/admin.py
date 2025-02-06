from django.contrib import admin
from .models import BotUser, Subscription  # Імпортуємо моделі

# Вбудована модель для підписок
class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1  # кількість порожніх рядків для додавання нових підписок
    fields = ['latitude', 'longitude', 'subscribed_at']  # Вказуємо поля для відображення

# Модель для відображення користувачів
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'name', 'date_at', 'has_subscription']  # Додаємо колонку для відображення наявності підписки
    search_fields = ['user_id', 'name']
    list_filter = ['date_at']  # Вказуємо лише фільтрацію за датою
    ordering = ['-date_at']
    inlines = [SubscriptionInline]  # Додаємо вбудовану модель для підписок

    # Метод для перевірки наявності підписки
    def has_subscription(self, obj):
        return obj.subscription_set.exists()  # Перевіряє, чи є підписка у користувача
    has_subscription.boolean = True  # Відображає як іконку (✓ або ✘)
    has_subscription.short_description = 'Підписка'

    # Метод для фільтрації користувачів з підписками
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Додаємо фільтр для підписаних користувачів
        if request.GET.get('has_subscription'):
            queryset = queryset.filter(subscription__isnull=False)
        return queryset

# Модель для відображення підписок
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'latitude', 'longitude', 'subscribed_at']
    search_fields = ['user__name', 'user__user_id']
    list_filter = ['subscribed_at']
    ordering = ['-subscribed_at']

# Реєструємо моделі в адмінці
admin.site.register(BotUser, BotUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
