from django.db import models
from django.utils import timezone

# Create your models here.
class PromptLog(models.Model):
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"PromptLog ({self.created_at}): {self.prompt[:30]}..."
