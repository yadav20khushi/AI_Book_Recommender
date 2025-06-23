from django.db import models
from django.utils import timezone
from apps.books.models import Book
from django.contrib.auth.models import User

class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class ChatHistory(models.Model):
    user_history = models.ForeignKey(UserHistory, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    messages = models.JSONField()

    def __str__(self):
        return f"{self.user_history.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


