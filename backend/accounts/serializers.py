from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    tier = serializers.SerializerMethodField()
    tokensRemaining = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'tier', 'tokensRemaining']

    def get_name(self, u):
        return u.first_name or u.username

    def get_tier(self, u):
        p = getattr(u, 'profile', None)
        return p.tier if p else None

    def get_tokensRemaining(self, u):
        p = getattr(u, 'profile', None)
        return p.tokens_remaining if p else 0


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
