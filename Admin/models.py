from django.db import models

class Message(models.Model):
    username = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.username} at {self.created_at}"
