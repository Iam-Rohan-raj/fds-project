from django.db import models
from django.utils import timezone
import string
import random


def generate_short_code():
    """Generate a unique 6-character short code."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))


class URL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=20, unique=True, default=generate_short_code)
    custom_alias = models.CharField(max_length=50, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    click_count = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_short_identifier()} -> {self.original_url[:50]}"

    def get_short_identifier(self):
        return self.custom_alias if self.custom_alias else self.short_code

    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def increment_clicks(self):
        self.click_count += 1
        self.save(update_fields=['click_count'])


class Click(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referer = models.URLField(max_length=2000, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"Click on {self.url.get_short_identifier()} at {self.clicked_at}"
