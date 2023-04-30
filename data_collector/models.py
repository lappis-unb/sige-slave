from django.db import models
from django.utils import timezone


class MemoryMap(models.Model):
    model = models.CharField()
    minutely = models.JSONField()
    quarterly = models.JSONField()
    monthly = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model

    class Meta:
        verbose_name_plural = "Memory Maps"
