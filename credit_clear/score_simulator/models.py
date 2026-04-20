from django.conf import settings
from django.db import models

from credit_clear.interventions.models import Intervention


class ScoreSimulation(models.Model):
    class SimulationType(models.TextChoices):
        INTERVENTION = "intervention", "Intervention Impact"
        WHAT_IF = "what_if", "What-If Scenario"
        FORECAST = "forecast", "Score Forecast"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="score_simulations")
    intervention = models.ForeignKey(Intervention, on_delete=models.SET_NULL, null=True, blank=True)
    simulation_type = models.CharField(max_length=20, choices=SimulationType.choices, default=SimulationType.INTERVENTION, db_index=True)
    current_score = models.PositiveSmallIntegerField()
    projected_score = models.PositiveSmallIntegerField()
    best_case_score = models.PositiveSmallIntegerField(null=True, blank=True)
    worst_case_score = models.PositiveSmallIntegerField(null=True, blank=True)
    avoided_damage_points = models.PositiveSmallIntegerField(default=0)
    score_factors_breakdown = models.JSONField(default=dict, blank=True)
    assumptions = models.JSONField(default=dict, blank=True)
    recommended_actions = models.JSONField(default=list, blank=True)
    horizon_days = models.PositiveIntegerField(default=90)
    model_version = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
