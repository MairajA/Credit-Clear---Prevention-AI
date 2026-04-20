from rest_framework import serializers

from credit_clear.score_simulator.models import ScoreSimulation


class ScoreSimulationSerializer(serializers.ModelSerializer):
    intervention_id = serializers.IntegerField(source="intervention.id", read_only=True, default=None)

    class Meta:
        model = ScoreSimulation
        fields = [
            "id",
            "intervention_id",
            "simulation_type",
            "current_score",
            "projected_score",
            "best_case_score",
            "worst_case_score",
            "avoided_damage_points",
            "score_factors_breakdown",
            "assumptions",
            "recommended_actions",
            "horizon_days",
            "model_version",
            "generated_at",
        ]
        read_only_fields = fields


class SimulateRequestSerializer(serializers.Serializer):
    simulation_type = serializers.ChoiceField(
        choices=ScoreSimulation.SimulationType.choices,
        default=ScoreSimulation.SimulationType.WHAT_IF,
    )
    scenario = serializers.DictField(
        required=False,
        help_text="Scenario parameters, e.g. {'action': 'pay_down', 'account_id': 1, 'target_balance': 500}",
    )
    horizon_days = serializers.IntegerField(default=90, min_value=30, max_value=365)


class WhatIfRequestSerializer(serializers.Serializer):
    """
    What-if scenarios the user can explore:
    - pay_down: "What if I pay Card X to $500?"
    - dispute_removed: "What if this dispute gets removed?"
    - miss_payment: "What if I miss this payment?"
    - open_account: "What if I open a secured card?"
    """

    action = serializers.ChoiceField(choices=[
        ("pay_down", "Pay Down Balance"),
        ("dispute_removed", "Dispute Removed"),
        ("miss_payment", "Miss Payment"),
        ("open_account", "Open New Account"),
    ])
    account_id = serializers.IntegerField(required=False, help_text="Linked account ID")
    target_balance = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        help_text="Target balance for pay_down scenario",
    )
