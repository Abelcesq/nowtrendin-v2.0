import os
import secrets
from datetime import timedelta

import requests

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Alert, GradeHistory, Watchlist, WatchlistItem, DashboardLayout
from .serializers import (
    SignupSerializer, UserSerializer, AlertSerializer,
    WatchlistSerializer, WatchlistItemSerializer,
)


class DashboardView(APIView):
    """GET/PUT the member's customizable dashboard layout (ordered tile configs).
    Stored per-user so it follows them across web, desktop, and mobile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        obj, _ = DashboardLayout.objects.get_or_create(user=request.user)
        return Response({'tiles': obj.tiles or [], 'favorites': obj.favorites or []})

    def put(self, request):
        obj, _ = DashboardLayout.objects.get_or_create(user=request.user)
        if 'tiles' in request.data:
            if not isinstance(request.data['tiles'], list):
                return Response({'detail': 'tiles must be a list'}, status=400)
            obj.tiles = request.data['tiles']
        if 'favorites' in request.data:
            if not isinstance(request.data['favorites'], list):
                return Response({'detail': 'favorites must be a list'}, status=400)
            obj.favorites = request.data['favorites']
        obj.save()
        return Response({'tiles': obj.tiles or [], 'favorites': obj.favorites or []})

TIER_TOKENS = {'consumer': 0, 'business': 0, 'enterprise': 100000}
# Monthly AI-grade credits per tier (grade ≈ $0.012 each; caps the exposure).
GRADE_TOKENS = {'consumer': 25, 'business': 250, 'enterprise': 100000}


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


class GoogleAuthView(APIView):
    """Sign in / sign up with a Google ID token from the mobile/web client.

    The client (expo-auth-session) obtains a Google ID token and posts it here.
    We verify the token's signature against Google's public keys and confirm the
    audience matches one of our OAuth client IDs, then get-or-create the user and
    issue our own JWT — identical shape to the password login response.
    No client secret needed (ID-token flow)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = (str(request.data.get('id_token') or request.data.get('idToken') or '')).strip()
        if not token:
            return Response({'detail': 'A Google id_token is required.'}, status=400)

        # Accept any of our platform client IDs as a valid audience.
        allowed = [
            os.environ.get('GOOGLE_WEB_CLIENT_ID', ''),
            os.environ.get('GOOGLE_IOS_CLIENT_ID', ''),
            os.environ.get('GOOGLE_ANDROID_CLIENT_ID', ''),
        ]
        allowed = [a for a in allowed if a]

        try:
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests as google_requests

            info = google_id_token.verify_oauth2_token(
                token, google_requests.Request()
            )
        except Exception as exc:
            return Response({'detail': f'Could not verify Google token: {exc}'}, status=401)

        if info.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
            return Response({'detail': 'Invalid token issuer.'}, status=401)
        if allowed and info.get('aud') not in allowed:
            return Response({'detail': 'Token was not issued for this app.'}, status=401)
        if not info.get('email_verified', False):
            return Response({'detail': 'Google email is not verified.'}, status=401)

        email = (info.get('email') or '').lower().strip()
        if not email:
            return Response({'detail': 'Google account has no email.'}, status=400)
        name = info.get('name') or info.get('given_name') or email.split('@')[0]

        user = (User.objects.filter(email__iexact=email).first()
                or User.objects.filter(username__iexact=email).first())
        created = False
        if user is None:
            user = User.objects.create_user(username=email, email=email, first_name=name)
            user.set_unusable_password()
            user.save()
            Profile.objects.create(user=user, tier=None)
            created = True
        else:
            Profile.objects.get_or_create(user=user)

        return Response(
            {'user': UserSerializer(user).data, 'created': created, **_tokens_for(user)},
            status=201 if created else 200,
        )


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
            profile.grade_tokens = GRADE_TOKENS.get(data['tier'], 0)
        if 'phone' in data:
            new_phone = (str(data['phone']).strip() or None) if data['phone'] is not None else None
            if new_phone != profile.phone:
                profile.phone = new_phone
                profile.phone_verified = False  # re-verification required (SMS OTP TBD)
        if 'notifyEmail' in data:
            profile.notify_email = bool(data['notifyEmail'])
        if 'notifyPush' in data:
            profile.notify_push = bool(data['notifyPush'])
        if 'notifySms' in data:
            profile.notify_sms = bool(data['notifySms'])
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


# Default points at the v2.0 engine — NEVER the frozen 1.0 app. Prod sets the
# GRADIENT_API config var explicitly; this fallback just keeps us off legacy 1.0.
GRADIENT_API = os.environ.get('GRADIENT_API', 'https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com')


class DirectQueryView(APIView):
    """Enterprise-only: score an arbitrary topic, deducting one query token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.tier != 'enterprise':
            return Response({'detail': 'Direct topic queries are an Enterprise feature.'}, status=403)
        if (profile.tokens_remaining or 0) <= 0:
            return Response({'detail': 'No query tokens remaining this month.'}, status=402)
        topic = (str(request.data.get('topic') or '')).strip()
        if not topic:
            return Response({'detail': 'A topic is required.'}, status=400)

        try:
            r = requests.post(f'{GRADIENT_API}/query', json={'topic': topic},
                              headers={'X-Internal-Key': settings.INTERNAL_API_KEY}, timeout=110)
            data = r.json()
        except Exception as exc:
            return Response({'detail': f'Scoring engine unavailable: {exc}'}, status=503)

        # Charge a token only when the engine actually returned a score.
        if data.get('found'):
            profile.tokens_remaining = max(0, (profile.tokens_remaining or 0) - 1)
            profile.save()
        data['tokensRemaining'] = profile.tokens_remaining
        return Response(data, status=200)


class PullTrendsView(APIView):
    """Enterprise-only: trigger a fresh trend collection + scoring run on the
    engine, deducting one query token. Mirrors the per-search token model so a
    'Pull Trends' costs exactly 1 token, same as a direct query."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.tier != 'enterprise':
            return Response({'detail': 'Pulling trends is an Enterprise feature.'}, status=403)
        if (profile.tokens_remaining or 0) <= 0:
            return Response({'detail': 'No query tokens remaining this month.'}, status=402)

        try:
            # /collect returns immediately; the engine runs the pipeline in the
            # background. We charge the token once the run is accepted.
            r = requests.post(f'{GRADIENT_API}/collect',
                              headers={'X-Internal-Key': settings.INTERNAL_API_KEY}, timeout=30)
            ok = r.status_code in (200, 202)
        except Exception as exc:
            return Response({'detail': f'Scoring engine unavailable: {exc}'}, status=503)

        if not ok:
            return Response({'detail': 'Engine did not accept the collection request.'},
                            status=502)

        profile.tokens_remaining = max(0, (profile.tokens_remaining or 0) - 1)
        profile.save()
        return Response(
            {'status': 'started',
             'message': 'Trend collection running. New scores appear shortly.',
             'tokensRemaining': profile.tokens_remaining},
            status=200,
        )


class PullMarketView(APIView):
    """Enterprise-only: trigger a fresh MARKET (risk/financial) collection on
    the engine, deducting one query token. Distinct from PullTrendsView — this
    runs the risk pipeline (FINRA short interest, OFR repo macro leverage,
    WhaleWisdom 13F, Finnhub insider + news, Alpha Vantage news sentiment,
    Yahoo Finance, creator + broadcast YouTube coverage). Trend-side sources
    (Apify Google Trends, X, GitHub, Hacker News, blogs, news APIs) belong on
    /api/pull-trends/. Separating the two keeps the cost ledger honest and the
    UX intuitive — Enterprise users pick which pipeline they want to refresh."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.tier != 'enterprise':
            return Response({'detail': 'Pulling market data is an Enterprise feature.'}, status=403)
        if (profile.tokens_remaining or 0) <= 0:
            return Response({'detail': 'No query tokens remaining this month.'}, status=402)

        try:
            # /risk/collect returns immediately; the engine runs the financial-side
            # pipeline in the background. Token charges once the run is accepted.
            r = requests.post(f'{GRADIENT_API}/risk/collect',
                              headers={'X-Internal-Key': settings.INTERNAL_API_KEY}, timeout=30)
            ok = r.status_code in (200, 202)
        except Exception as exc:
            return Response({'detail': f'Scoring engine unavailable: {exc}'}, status=503)

        if not ok:
            return Response({'detail': 'Engine did not accept the market-collection request.'},
                            status=502)

        profile.tokens_remaining = max(0, (profile.tokens_remaining or 0) - 1)
        profile.save()
        return Response(
            {'status': 'started',
             'message': 'Market collection running. New positioning scores appear shortly.',
             'tokensRemaining': profile.tokens_remaining},
            status=200,
        )


class GradeView(APIView):
    """AI-grade a topic not in our data (Perplexity research + Claude synthesis).
    Available on ALL tiers, metered by a monthly grade-token allowance
    (Consumer 25 / Business 250 / Enterprise 1000). One grade token is charged
    only when a proposed score actually returns."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.tier:
            return Response({'detail': 'Choose a membership plan to use AI grading.'}, status=403)
        if (profile.grade_tokens or 0) <= 0:
            return Response({'detail': 'No AI-grade credits remaining this month.',
                             'gradeTokens': 0}, status=402)
        topic = (str(request.data.get('topic') or '')).strip()
        if not topic:
            return Response({'detail': 'A topic is required.'}, status=400)

        try:
            r = requests.post(f'{GRADIENT_API}/grade', json={'topic': topic},
                              headers={'X-Internal-Key': settings.INTERNAL_API_KEY}, timeout=120)
            data = r.json()
        except Exception as exc:
            return Response({'detail': f'AI grade engine unavailable: {exc}'}, status=503)

        # The Grade Agent searches our data pool first. A 'measured' result is the
        # engine's OWN score (no AI ran) — it is FREE (charge_token=False). Only an
        # AI-PROPOSED grade burns a credit. Honour the agent's charge_token flag,
        # falling back to the legacy "proposed score returned" rule.
        charge = data.get('charge_token')
        if charge is None:
            charge = bool(data.get('available') and data.get('proposed')
                          and data.get('source') != 'measured')
        if charge:
            profile.grade_tokens = max(0, (profile.grade_tokens or 0) - 1)
            profile.save()
        # Persist to history whenever a real score came back (measured OR proposed),
        # so both populate the History + Graded tabs.
        if data.get('available') and data.get('proposed'):
            try:
                GradeHistory.objects.create(
                    user=request.user, topic=topic[:200],
                    detection=float(data.get('detection_score') or 0),
                    confidence=float(data.get('confidence_score') or 0),
                    stage=str(data.get('stage') or '')[:24],
                    result_json=data,
                )
            except Exception:
                pass
        data['gradeTokens'] = profile.grade_tokens
        return Response(data, status=200)


def _serialize_grade(g):
    return {
        'id': g.id, 'topic': g.topic,
        'detection': round(g.detection, 1), 'confidence': round(g.confidence, 1),
        'stage': g.stage, 'createdAt': g.created_at.isoformat(),
        'result': g.result_json,
    }


class GradeHistoryView(APIView):
    """The signed-in user's own grade history — last 12 months, newest first.
    No token charge (just reading). Optional ?q= substring search on topic."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cutoff = timezone.now() - timedelta(days=365)
        qs = GradeHistory.objects.filter(user=request.user, created_at__gte=cutoff)
        q = (request.query_params.get('q') or '').strip()
        if q:
            qs = qs.filter(topic__icontains=q)
        qs = qs.order_by('-created_at')[:500]
        return Response({'grades': [_serialize_grade(g) for g in qs]}, status=200)


class GradedAllView(APIView):
    """All topics graded by ANY member (across all tiers) — the community 'Graded'
    list. Deduped to the latest grade per topic, newest first. No token charge.
    Optional ?q= substring search."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = (request.query_params.get('q') or '').strip()
        qs = GradeHistory.objects.all()
        if q:
            qs = qs.filter(topic__icontains=q)
        # Latest grade per (case-insensitive) topic.
        seen = {}
        for g in qs.order_by('-created_at')[:2000]:
            key = g.topic.strip().lower()
            if key not in seen:
                seen[key] = g
            if len(seen) >= 300:
                break
        items = sorted(seen.values(), key=lambda g: g.created_at, reverse=True)
        return Response({'grades': [_serialize_grade(g) for g in items]}, status=200)


def _notify_alert(alert, current):
    """Deliver a fired alert. Email + text now; push requires an Expo push token
    (dev build). Text fires only when the alert opts into SMS AND the user has a
    verified phone — otherwise SMS is silently skipped."""
    user = alert.user
    label = alert.topic_display or alert.topic_key
    below = getattr(alert, 'direction', 'above') == 'below'
    if alert.notify_email and user.email:
        try:
            send_mail(
                subject=f"Now TrendIn alert: {label} {'fell to' if below else 'hit'} {current}",
                message=(
                    f"'{label}' just {'dropped to' if below else 'reached'} a {alert.score_type} "
                    f"Gradient Score of {current} "
                    f"(your threshold was {alert.threshold}, direction: "
                    f"{'falls below' if below else 'rises above'}).\n\n"
                    f"Open Now TrendIn to see the full signal."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    if getattr(alert, 'notify_sms', False):
        profile = getattr(user, 'profile', None)
        if profile and profile.phone_verified and profile.phone:
            _send_sms(
                profile.phone,
                f"Now TrendIn: {label} hit a {alert.score_type} score of {current} "
                f"(threshold {alert.threshold}).",
            )


def _notify_watchlist(wl, crossed):
    """Deliver a watchlist movement notification (email + text) listing the items
    that crossed the list's Detection threshold. Text only if phone verified."""
    user = wl.user
    names = ', '.join(c['label'] for c in crossed[:6])
    more = f" (+{len(crossed) - 6} more)" if len(crossed) > 6 else ''
    body_lines = '\n'.join(f"  • {c['label']}: Detection {c['score']}" for c in crossed[:12])
    if wl.notify_email and user.email:
        try:
            send_mail(
                subject=f"Now TrendIn watchlist '{wl.name}': {len(crossed)} item(s) moving",
                message=(
                    f"These items on your '{wl.name}' watchlist crossed Detection "
                    f"{wl.notify_threshold}:\n\n{body_lines}\n\nOpen Now TrendIn for the full signal."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    if wl.notify_sms:
        profile = getattr(user, 'profile', None)
        if profile and profile.phone_verified and profile.phone:
            _send_sms(profile.phone, f"Now TrendIn '{wl.name}': {names}{more} crossing Detection {wl.notify_threshold}.")


class EvaluateAlertsView(APIView):
    """Internal: pull live scores and fire any active alert whose threshold is
    crossed, plus any watchlist whose items cross its movement threshold."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.headers.get('X-Internal-Key') != settings.INTERNAL_API_KEY:
            return Response({'detail': 'forbidden'}, status=403)
        try:
            r = requests.get(f'{GRADIENT_API}/scores', params={'limit': 200}, timeout=30)
            results = r.json().get('results', [])
        except Exception as exc:
            return Response({'detail': f'engine unavailable: {exc}'}, status=503)

        scores = {}
        for row in results:
            scores[row.get('topic_key')] = {
                'detection': round(row.get('detection_score', 0) or 0),
                'confidence': round(row.get('confidence_score', 0) or 0),
                'overall': round(row.get('overall_score', 0) or 0),
            }

        # Market (risk) detection scores — for watchlist 'market' items. Best-effort.
        market = {}
        try:
            rr = requests.get(f'{GRADIENT_API}/risk/scores', params={'limit': 200}, timeout=30)
            for row in rr.json().get('results', []):
                market[row.get('risk_topic')] = round(row.get('detection_score', 0) or 0)
        except Exception:
            pass

        now = timezone.now()
        cooldown = now - timedelta(hours=6)
        fired = 0
        active = Alert.objects.filter(active=True)
        for alert in active:
            if alert.kind == 'market':
                # Market alerts evaluate against the market (risk) Detection score.
                mv = market.get(alert.topic_key)
                if mv is None:
                    continue
                current = mv
            else:
                s = scores.get(alert.topic_key)
                if not s:
                    continue
                current = s.get(alert.score_type, s['detection'])
            # falls-below alerts (2026-07-19): 'below' fires when the score drops to
            # or under the threshold; 'above' keeps the original >= behavior.
            crossed = (current <= alert.threshold if getattr(alert, 'direction', 'above') == 'below'
                       else current >= alert.threshold)
            fresh = alert.last_triggered_at is None or alert.last_triggered_at < cooldown
            if crossed and fresh:
                alert.last_triggered_at = now
                alert.save(update_fields=['last_triggered_at'])
                _notify_alert(alert, current)
                fired += 1

        # Watchlist movement notifications — any list opting into email/text whose
        # items cross its Detection threshold. One digest per list, 6h cooldown.
        wl_fired = 0
        from django.db.models import Q
        lists = (Watchlist.objects.filter(Q(notify_email=True) | Q(notify_sms=True))
                 .prefetch_related('items'))
        for wl in lists:
            fresh = wl.last_notified_at is None or wl.last_notified_at < cooldown
            if not fresh:
                continue
            crossed = []
            for item in wl.items.all():
                if item.kind == 'market':
                    sc = market.get(item.key)
                else:
                    s = scores.get(item.key)
                    sc = s['detection'] if s else None
                if sc is not None and sc >= wl.notify_threshold:
                    crossed.append({'label': item.display or item.key, 'score': sc})
            if crossed:
                wl.last_notified_at = now
                wl.save(update_fields=['last_notified_at'])
                _notify_watchlist(wl, crossed)
                wl_fired += 1

        return Response({'fired': fired, 'checked': active.count(),
                         'watchlists_fired': wl_fired})


class ResetCreditsView(APIView):
    """Internal: reset every profile's monthly query + AI-grade credits to its
    tier allowance. Called monthly by the engine scheduler (X-Internal-Key)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.headers.get('X-Internal-Key') != settings.INTERNAL_API_KEY:
            return Response({'detail': 'forbidden'}, status=403)
        from .credits import reset_all_credits
        counts = reset_all_credits()
        return Response({'status': 'reset', 'counts': counts})


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


class ForgotPasswordView(APIView):
    """Email a 6-digit password-reset code. Always 200 (don't leak account existence)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (str(request.data.get('email') or '')).lower().strip()
        if email:
            user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
            if user:
                profile, _ = Profile.objects.get_or_create(user=user)
                code = f'{secrets.randbelow(900000) + 100000}'
                profile.reset_code = code
                profile.reset_expires = timezone.now() + timedelta(minutes=15)
                profile.save()
                try:
                    send_mail(
                        subject='Your Now TrendIn password reset code',
                        message=f'Your password reset code is {code}. It expires in 15 minutes.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email or email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
        return Response({'detail': 'If that email exists, a reset code is on its way.'})


class ResetPasswordView(APIView):
    """Confirm the reset code and set a new password."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (str(request.data.get('email') or '')).lower().strip()
        code = (str(request.data.get('code') or '')).strip()
        new = request.data.get('password') or ''
        user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
        if not user:
            return Response({'detail': 'Invalid email or code.'}, status=400)
        profile, _ = Profile.objects.get_or_create(user=user)
        if not profile.reset_code or not profile.reset_expires:
            return Response({'detail': 'Request a reset code first.'}, status=400)
        if timezone.now() > profile.reset_expires:
            return Response({'detail': 'Code expired. Request a new one.'}, status=400)
        if code != profile.reset_code:
            return Response({'detail': 'Incorrect code.'}, status=400)
        if len(new) < 8:
            return Response({'detail': 'Password must be at least 8 characters.'}, status=400)
        user.set_password(new)
        user.save()
        profile.reset_code = None
        profile.reset_expires = None
        profile.save()
        return Response({'detail': 'Password updated. You can sign in now.'})


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


# ── Watchlists — per-user, backend-synced so the SAME lists appear on web,
# desktop, and mobile. Items store only a key/display/kind; the client looks up
# the live Detection/Confidence so scores are never stale. ──
class WatchlistListCreate(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).prefetch_related('items')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WatchlistDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).prefetch_related('items')


class WatchlistItemCreate(APIView):
    """POST /api/watchlists/<id>/items/  — add an item to one of the user's lists."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            wl = Watchlist.objects.get(pk=pk, user=request.user)
        except Watchlist.DoesNotExist:
            return Response({'detail': 'Watchlist not found.'}, status=404)
        key = (request.data.get('key') or '').strip()
        if not key:
            return Response({'detail': 'key is required.'}, status=400)
        item, _ = WatchlistItem.objects.get_or_create(
            watchlist=wl, key=key,
            defaults={'display': (request.data.get('display') or '').strip(),
                      'kind': request.data.get('kind') or 'topic'},
        )
        return Response(WatchlistItemSerializer(item).data, status=201)


class WatchlistItemDetail(APIView):
    """DELETE /api/watchlists/<id>/items/<item_id>/  — remove an item."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, item_id):
        deleted, _ = WatchlistItem.objects.filter(
            id=item_id, watchlist__id=pk, watchlist__user=request.user).delete()
        if not deleted:
            return Response({'detail': 'Item not found.'}, status=404)
        return Response(status=204)
