from django.urls import path

from .views import SimulateView
from .views import SimulationDetailView
from .views import SimulationListView
from .views import WhatIfView

app_name = "score_simulator_api"

urlpatterns = [
    path("simulate/", SimulateView.as_view(), name="simulate"),
    path("what-if/", WhatIfView.as_view(), name="what_if"),
    path("simulations/", SimulationListView.as_view(), name="simulation_list"),
    path("simulations/<int:pk>/", SimulationDetailView.as_view(), name="simulation_detail"),
]
