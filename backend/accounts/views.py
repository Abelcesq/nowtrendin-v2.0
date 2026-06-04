import os
import secrets
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Alert
from .serializers import SignupSerializer, UserSerializer, AlertSerializer

TIER_TOKENS = {'consumer': 0, 'business': 0, 'enterprise': 1000}


def _send_sms(to, body):
    """Send an SMS via Twilio. Returns (ok, error_message)."""
    sid = os.environ.get('TWILIO_ACCOUNT_SID')
    token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_FROM_NUMBER')
    if not (sid and token and from_number):
        return False, 'SMS is not configured yet.'
    try:
        from twilio.rest import Client
        Client(sid, token).messages.create(to=to, from_=from_number, body=body)
        return True, None
    except Exception as exc:
        return False, f'Could not send SMS: {exc}'


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
        if 'notifyEmail' in data:
            profile.notify_email = bool(data['notifyEmail'])
        if 'notifyPush' in data:
            profile.notify_push = bool(data['notifyPush'])
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


class AlertListCreate(generics.ListCreateAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlertDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)


class SendPhoneCodeView(APIView):
    """Send a 6-digit SMS verification code to the user's phone (2FA)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        phone = (str(request.data.get('phone') or profile.phone or '')).strip()
        if not phone:
            return Response({'detail': 'Add a phone number first.'}, status=400)

        code = f'{secrets.randbelow(900000) + 100000}'
        profile.phone = phone
        profile.otp_code = code
        profile.otp_expires = timezone.now() + timedelta(minutes=10)
        profile.phone_verified = False
        profile.save()

        ok, err = _send_sms(phone, f'Your Now TrendIn verification code is {code}. It expires in 10 minutes.')
        if not ok:
            return Response({'detail': err}, status=503)
        return Response({'detail': 'Verification code sent.'})


class VerifyPhoneView(APIView):
    """Confirm the SMS code and mark the phone verified."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = (str(request.data.get('code') or '')).strip()
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.otp_code or not profile.otp_expires:
            return Response({'detail': 'Request a code first.'}, status=400)
        if timezone.now() > profile.otp_expires:
            return Response({'detail': 'Code expired. Request a new one.'}, status=400)
        if code != profile.otp_code:
            return Response({'detail': 'Incorrect code.'}, status=400)
        profile.phone_verified = True
        profile.otp_code = None
        profile.otp_expires = None
        profile.save()
        return Response({'user': UserSerializer(request.user).data})
