from __future__ import annotations

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from credit_clear.score_simulator.models import ScoreSimulation
from credit_clear.utils.auth import bearer_auth
from credit_clear.utils.response import created
from credit_clear.utils.response import not_found
from credit_clear.utils.response import success
from credit_clear.utils.response import validation_error

from .serializers import ScoreSimulationSerializer
from .serializers import SimulateRequestSerializer
from .serializers import WhatIfRequestSerializer

logger = logging.getLogger(__name__)


class SimulationListView(APIView):
    """
    GET /api/v1/score-simulator/simulations/
    List past score simulations.

    Query params:
        simulation_type: intervention | what_if | forecast
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = (
            ScoreSimulation.objects
            .filter(user=user)
            .select_related("intervention")
            .order_by("-generated_at")
        )

        sim_type = request.query_params.get("simulation_type")
        if sim_type:
            qs = qs.filter(simulation_type=sim_type)

        serializer = ScoreSimulationSerializer(qs[:50], many=True)
        return success(serializer.data)


class SimulationDetailView(APIView):
    """
    GET /api/v1/score-simulator/simulations/{id}/
    """

    def get(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            sim = ScoreSimulation.objects.select_related("intervention").get(pk=pk, user=user)
        except ScoreSimulation.DoesNotExist:
            return not_found("Simulation not found.")

        serializer = ScoreSimulationSerializer(sim)
        return success(serializer.data)


@method_decorator(csrf_exempt, name="dispatch")
class SimulateView(APIView):
    """
    POST /api/v1/score-simulator/simulate/
    Run a general score simulation.

    Request body:
    {
        "simulation_type": "forecast",
        "scenario": {},
        "horizon_days": 90
    }
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        serializer = SimulateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        data = serializer.validated_data

        # Get current score from latest analysis
        from credit_clear.ai_engine.models import CreditAnalysis
        latest = CreditAnalysis.objects.filter(user=user).order_by("-generated_at").first()
        current_score = latest.credit_score if latest else 620  # fallback

        # In production: run through Score Simulator ML model
        # For now: compute placeholder projection
        projected = min(current_score + 23, 850)
        best_case = min(current_score + 45, 850)
        worst_case = max(current_score - 10, 300)

        sim = ScoreSimulation.objects.create(
            user=user,
            simulation_type=data["simulation_type"],
            current_score=current_score,
            projected_score=projected,
            best_case_score=best_case,
            worst_case_score=worst_case,
            avoided_damage_points=0,
            score_factors_breakdown={
                "payment_history": "+10 (on-time payments maintained)",
                "utilization": "+8 (reduced utilization)",
                "credit_age": "+3 (aging accounts)",
                "credit_mix": "+2 (diversified mix)",
                "inquiries": "0 (no new inquiries)",
            },
            assumptions=data.get("scenario", {}),
            recommended_actions=[
                "Pay Discover card below 30% utilization for +25 points",
                "File dispute on incorrect Chase balance for +15 points",
                "Maintain on-time payments for next 90 days",
            ],
            horizon_days=data["horizon_days"],
            model_version="ss-v1.0.0",
        )

        logger.info("Score simulation: user=%s type=%s sim_id=%s", user.id, data["simulation_type"], sim.id)
        result = ScoreSimulationSerializer(sim)
        return created(result.data)


@method_decorator(csrf_exempt, name="dispatch")
class WhatIfView(APIView):
    """
    POST /api/v1/score-simulator/what-if/
    Run a what-if scenario simulation.

    Request body:
    {
        "action": "pay_down",
        "account_id": 1,
        "target_balance": 500
    }
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        serializer = WhatIfRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        data = serializer.validated_data
        action = data["action"]

        # Get current score
        from credit_clear.ai_engine.models import CreditAnalysis
        latest = CreditAnalysis.objects.filter(user=user).order_by("-generated_at").first()
        current_score = latest.credit_score if latest else 620

        # In production: each action type runs through the ML model
        # For now: action-specific placeholder logic
        impact_map = {
            "pay_down": {"projected": 25, "best": 40, "worst": 10, "msg": "Pay down balance"},
            "dispute_removed": {"projected": 20, "best": 35, "worst": 0, "msg": "Dispute removed from report"},
            "miss_payment": {"projected": -45, "best": -30, "worst": -75, "msg": "Missed payment impact"},
            "open_account": {"projected": 5, "best": 15, "worst": -10, "msg": "New account opened"},
        }
        impact = impact_map.get(action, {"projected": 0, "best": 0, "worst": 0, "msg": action})

        projected = max(300, min(850, current_score + impact["projected"]))
        best_case = max(300, min(850, current_score + impact["best"]))
        worst_case = max(300, min(850, current_score + impact["worst"]))

        sim = ScoreSimulation.objects.create(
            user=user,
            simulation_type=ScoreSimulation.SimulationType.WHAT_IF,
            current_score=current_score,
            projected_score=projected,
            best_case_score=best_case,
            worst_case_score=worst_case,
            avoided_damage_points=abs(impact["worst"]) if impact["projected"] < 0 else 0,
            score_factors_breakdown={
                "primary_factor": impact["msg"],
                "projected_change": impact["projected"],
            },
            assumptions=data,
            recommended_actions=[
                f"Scenario: {impact['msg']}",
                f"Expected change: {impact['projected']:+d} points",
                f"Best case: {impact['best']:+d} points / Worst case: {impact['worst']:+d} points",
            ],
            horizon_days=90,
            model_version="ss-v1.0.0",
        )

        logger.info("What-if simulation: user=%s action=%s sim_id=%s", user.id, action, sim.id)
        result = ScoreSimulationSerializer(sim)
        return created(result.data)
