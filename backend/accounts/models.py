from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Extra per-user data: membership tier + query tokens."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tier = models.CharField(max_length=20, null=True, blank=True)  # consumer / business / enterprise
    tokens_remaining = models.IntegerField(default=0)
    phone = models.CharField(max_length=20, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_expires = models.DateTimeField(null=True, blank=True)
    reset_code = models.CharField(max_length=6, null=True, blank=True)
    reset_expires = models.DateTimeField(null=True, blank=True)
    notify_email = models.BooleanField(default=True)
    notify_push = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ({self.tier or 'no tier'})"


class Alert(models.Model):
    SCORE_TYPES = [('detection', 'detection'), ('confidence', 'confidence'), ('overall', 'overall')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    topic_key = models.CharField(max_length=120)
    topic_display = models.CharField(max_length=160, blank=True)
    score_type = models.CharField(max_length=12, choices=SCORE_TYPES, default='detection')
    threshold = models.IntegerField(default=75)
    notify_email = models.BooleanField(default=True)
    notify_push = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic_display or self.topic_key} >= {self.threshold} ({self.user.email})"
