from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Extra per-user data: membership tier + query tokens."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tier = models.CharField(max_length=20, null=True, blank=True)  # consumer / business / enterprise
    tokens_remaining = models.IntegerField(default=0)        # query tokens (Enterprise)
    grade_tokens = models.IntegerField(default=0)            # monthly AI-grade credits (all tiers)
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


class GradeHistory(models.Model):
    """Every AI-grade result a user obtains. Per-user history (12-month retention)
    powers the 'History' tab; the union across users powers the 'Graded' tab."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    topic = models.CharField(max_length=200)
    detection = models.FloatField(default=0)
    confidence = models.FloatField(default=0)
    stage = models.CharField(max_length=24, blank=True)
    result_json = models.JSONField(default=dict)   # full proposed-score payload
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['topic']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.topic} ({self.user.email} · {self.created_at:%Y-%m-%d})"


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


class Watchlist(models.Model):
    """A user's saved list of topics/instruments to track. Per-user, synced via
    the backend so the SAME lists appear on web, desktop, and mobile."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class WatchlistItem(models.Model):
    """One tracked entry inside a watchlist. `kind` distinguishes an attention
    Trend ('topic') from a Market Signal instrument ('market'); the client looks
    up the live score by `key`, so we never store stale scores."""
    KINDS = [('topic', 'topic'), ('market', 'market')]
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='items')
    key = models.CharField(max_length=120)            # topic_key or risk_topic
    display = models.CharField(max_length=160, blank=True)
    kind = models.CharField(max_length=12, choices=KINDS, default='topic')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']
        unique_together = ('watchlist', 'key')

    def __str__(self):
        return f"{self.display or self.key} in {self.watchlist.name}"


class DashboardLayout(models.Model):
    """Per-user customizable dashboard — an ordered list of tile configs (built-in
    tiles + user-created custom 'metric' tiles). Saved server-side so the layout
    follows the member across web, desktop, and mobile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard')
    tiles = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)
