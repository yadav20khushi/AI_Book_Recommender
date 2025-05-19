from django.db import models
from django.utils import timezone
from apps.books.models import Book

# Create your models here.
class PromptLog(models.Model):
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"PromptLog ({self.created_at}): {self.prompt[:30]}..."

class RecommendedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    prompt_log = models.ForeignKey("PromptLog", on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.rank}. {self.book.title} ({self.prompt_log.created_at})"
