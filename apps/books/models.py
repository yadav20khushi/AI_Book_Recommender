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
'''
    Have to write a script to fetch lib data from 
    https://data4library.kr/api/libSrch?authKey=auth_key&format=json
    and save to Library db
'''
class Library(models.Model):
    name = models.CharField(max_length=255)
    lib_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.lib_code})"
