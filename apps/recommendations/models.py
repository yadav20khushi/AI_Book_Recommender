from django.db import models
from django.utils import timezone
from apps.books.models import Book

# Create your models here.

class UserHistory(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128, default="temp123")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

class ChatHistory(models.Model):
    user = models.ForeignKey("UserHistory", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    messages = models.JSONField()

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

