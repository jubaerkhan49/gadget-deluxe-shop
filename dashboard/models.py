from django.db import models
from django.contrib.auth.models import User


class PageVisit(models.Model):
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    path = models.CharField(max_length=255, db_index=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    referer = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Page Visit"
        verbose_name_plural = "Page Visits"

    def __str__(self):
        return f"{self.path} - {self.ip_address} @ {self.timestamp:%Y-%m-%d %H:%M}"
