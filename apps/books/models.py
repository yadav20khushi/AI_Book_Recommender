from django.db import models

# Create your models here.
class Book(models.Model):
    isbn13 = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    cover_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
