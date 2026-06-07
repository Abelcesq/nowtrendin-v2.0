"""One-off SMTP delivery test. Run:
heroku run -a nowtrendin-backend python test_email.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("EMAIL_BACKEND   :", settings.EMAIL_BACKEND)
print("EMAIL_HOST      :", getattr(settings, "EMAIL_HOST", None))
print("EMAIL_HOST_USER :", getattr(settings, "EMAIL_HOST_USER", None))
print("FROM            :", settings.DEFAULT_FROM_EMAIL)

# fail_silently=False so any SMTP/auth error is raised and visible.
sent = send_mail(
    subject="Now TrendIn — SMTP test",
    message="If you can read this, password-reset email delivery is live. ✅",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["Support@NowTrendin.com"],
    fail_silently=False,
)
print("send_mail returned:", sent, "(1 = accepted by server)")
