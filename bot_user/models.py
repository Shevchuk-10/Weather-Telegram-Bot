from django.db import models


class BotUser(models.Model):
    user_id = models.CharField(max_length=64, unique=True)
    date_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=64,)

    def __str__(self):
        return self.name


