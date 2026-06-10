from django.contrib import admin
from django.urls import path, include

from accounts.views import AlertListCreate, AlertDetail, DirectQueryView, EvaluateAlertsView, PullTrendsView, PullMarketView, GradeView, GradeHistoryView, GradedAllView, ResetCreditsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/alerts/', AlertListCreate.as_view()),
    path('api/alerts/<int:pk>/', AlertDetail.as_view()),
    path('api/query/', DirectQueryView.as_view()),
    path('api/pull-trends/', PullTrendsView.as_view()),
    path('api/pull-market/', PullMarketView.as_view()),
    path('api/grade/', GradeView.as_view()),
    path('api/grade/history/', GradeHistoryView.as_view()),
    path('api/grade/all/', GradedAllView.as_view()),
    path('api/internal/evaluate-alerts/', EvaluateAlertsView.as_view()),
    path('api/internal/reset-credits/', ResetCreditsView.as_view()),
    path('api/', include('todos.urls')),
]
