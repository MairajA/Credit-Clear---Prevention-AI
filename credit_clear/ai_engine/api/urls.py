from django.urls import path

from .views import AnalysisDetailView
from .views import AnalysisLatestView
from .views import AnalysisListView
from .views import RecoveryPlanDetailView
from .views import RecoveryPlanGenerateView
from .views import RecoveryPlanListView
from .views import ReportPullCreateView
from .views import ReportPullDetailView
from .views import ReportPullListView

app_name = "ai_engine_api"

urlpatterns = [
    # Credit Report Pulls
    path("report-pulls/", ReportPullListView.as_view(), name="report_pull_list"),
    path("report-pulls/new/", ReportPullCreateView.as_view(), name="report_pull_create"),
    path("report-pulls/<int:pk>/", ReportPullDetailView.as_view(), name="report_pull_detail"),
    # Credit Analysis
    path("analyses/", AnalysisListView.as_view(), name="analysis_list"),
    path("analyses/latest/", AnalysisLatestView.as_view(), name="analysis_latest"),
    path("analyses/<int:pk>/", AnalysisDetailView.as_view(), name="analysis_detail"),
    # Recovery Plans
    path("recovery-plans/", RecoveryPlanListView.as_view(), name="recovery_plan_list"),
    path("recovery-plans/generate/", RecoveryPlanGenerateView.as_view(), name="recovery_plan_generate"),
    path("recovery-plans/<int:pk>/", RecoveryPlanDetailView.as_view(), name="recovery_plan_detail"),
]
