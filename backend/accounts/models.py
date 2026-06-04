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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ({self.tier or 'no tier'})"
