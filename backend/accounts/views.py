from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .serializers import SignupSerializer, UserSerializer

TIER_TOKENS = {'consumer': 0, 'business': 0, 'enterprise': 1000}


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'user': UserSerializer(user).data, **_tokens_for(user)},
            status=201,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').lower().strip()
        password = request.data.get('password') or ''
        user = authenticate(username=email, password=password)
        if user is None:
            # Fall back to email lookup (in case username != email)
            try:
                u = User.objects.get(email__iexact=email)
                user = authenticate(username=u.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is None:
            return Response({'detail': 'Incorrect email or password'}, status=400)
        return Response({'user': UserSerializer(user).data, **_tokens_for(user)})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'user': UserSerializer(request.user).data})

    def patch(self, request):
        """Update profile: tier, name, email, phone."""
        user = request.user
        data = request.data

        if 'name' in data and data['name']:
            user.first_name = str(data['name']).strip()

        if 'email' in data and data['email']:
            email = str(data['email']).lower().strip()
            if email != user.email:
                clash = (
                    User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists()
                    or User.objects.filter(username__iexact=email).exclude(pk=user.pk).exists()
                )
                if clash:
                    return Response({'email': ['This email is already in use']}, status=400)
                user.email = email
                user.username = email
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        if data.get('tier') is not None:
            profile.tier = data['tier']
            profile.tokens_remaining = TIER_TOKENS.get(data['tier'], 0)
        if 'phone' in data:
            new_phone = (str(data['phone']).strip() or None) if data['phone'] is not None else None
            if new_phone != profile.phone:
                profile.phone = new_phone
                profile.phone_verified = False  # re-verification required (SMS OTP TBD)
        profile.save()

        return Response({'user': UserSerializer(user).data})


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current = request.data.get('current_password') or ''
        new = request.data.get('new_password') or ''
        if not request.user.check_password(current):
            return Response({'detail': 'Current password is incorrect'}, status=400)
        if len(new) < 8:
            return Response({'detail': 'New password must be at least 8 characters'}, status=400)
        request.user.set_password(new)
        request.user.save()
        return Response({'detail': 'Password updated'})
