from django.urls import path

from .views import RiskAlertAcknowledgeView
from .views import RiskAlertDetailView
from .views import RiskAlertListView
from .views import RiskDashboardView
from .views import RiskScoreDetailView
from .views import RiskScoreLatestView
from .views import RiskScoreListView

app_name = "risk_monitoring_api"

urlpatterns = [
    # Risk Scores
    path("scores/", RiskScoreListView.as_view(), name="score_list"),
    path("scores/latest/", RiskScoreLatestView.as_view(), name="score_latest"),
    path("scores/<int:pk>/", RiskScoreDetailView.as_view(), name="score_detail"),
    # Risk Alerts
    path("alerts/", RiskAlertListView.as_view(), name="alert_list"),
    path("alerts/<int:pk>/", RiskAlertDetailView.as_view(), name="alert_detail"),
    path("alerts/<int:pk>/acknowledge/", RiskAlertAcknowledgeView.as_view(), name="alert_acknowledge"),
    # Dashboard
    path("dashboard/", RiskDashboardView.as_view(), name="dashboard"),
]
