from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile, Alert


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    tier = serializers.SerializerMethodField()
    tokensRemaining = serializers.SerializerMethodField()
    gradeTokens = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    phoneVerified = serializers.SerializerMethodField()
    notifyEmail = serializers.SerializerMethodField()
    notifyPush = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'tier', 'tokensRemaining', 'gradeTokens', 'phone', 'phoneVerified', 'notifyEmail', 'notifyPush']

    def get_gradeTokens(self, u):
        p = getattr(u, 'profile', None)
        return p.grade_tokens if p else 0

    def get_notifyEmail(self, u):
        p = getattr(u, 'profile', None)
        return bool(p.notify_email) if p else True

    def get_notifyPush(self, u):
        p = getattr(u, 'profile', None)
        return bool(p.notify_push) if p else True

    def get_name(self, u):
        return u.first_name or u.username

    def get_tier(self, u):
        p = getattr(u, 'profile', None)
        return p.tier if p else None

    def get_tokensRemaining(self, u):
        p = getattr(u, 'profile', None)
        return p.tokens_remaining if p else 0

    def get_phone(self, u):
        p = getattr(u, 'profile', None)
        return p.phone if p else None

    def get_phoneVerified(self, u):
        p = getattr(u, 'profile', None)
        return bool(p.phone_verified) if p else False


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, v):
        v = v.lower().strip()
        if User.objects.filter(username__iexact=v).exists() or User.objects.filter(email__iexact=v).exists():
            raise serializers.ValidationError('This email is already registered')
        return v

    def create(self, data):
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            first_name=data['name'],
            password=data['password'],
        )
        Profile.objects.create(user=user, tier=None)
        return user


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            'id', 'topic_key', 'topic_display', 'score_type', 'threshold',
            'notify_email', 'notify_push', 'active', 'last_triggered_at', 'created_at',
        ]
        read_only_fields = ['id', 'last_triggered_at', 'created_at']
