from django.contrib import admin
from django.urls import path, include

from accounts.views import AlertListCreate, AlertDetail, DirectQueryView, EvaluateAlertsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/alerts/', AlertListCreate.as_view()),
    path('api/alerts/<int:pk>/', AlertDetail.as_view()),
    path('api/query/', DirectQueryView.as_view()),
    path('api/internal/evaluate-alerts/', EvaluateAlertsView.as_view()),
    path('api/', include('todos.urls')),
]
