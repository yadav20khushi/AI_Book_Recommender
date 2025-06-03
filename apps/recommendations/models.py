from django.db import models
from django.utils import timezone
from apps.books.models import Book

# Create your models here.

class UserHistory(models.Model):
    username = models.CharField(max_length=100)  # or use ForeignKey if auth
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    session_start = models.DateTimeField()
    session_end = models.DateTimeField()

    def session_duration(self):
        return self.session_end - self.session_start

    def __str__(self):
        return f"{self.username} selected {self.book.title} on {self.session_end}"

