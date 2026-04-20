from django.conf import settings
from django.db import models

from credit_clear.accounts.models import LinkedAccount


class CreditNode(models.Model):
    class NodeType(models.TextChoices):
        USER = "user", "User"
        ACCOUNT = "account", "Account"
        DEBT = "debt", "Debt"
        BILL = "bill", "Bill"
        CREDITOR = "creditor", "Creditor"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_nodes")
    node_type = models.CharField(max_length=20, choices=NodeType.choices, db_index=True)
    linked_account = models.ForeignKey(LinkedAccount, on_delete=models.CASCADE, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, db_index=True)
    title = models.CharField(max_length=255)
    attributes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "node_type"]), models.Index(fields=["user", "external_id"])]


class CreditEdge(models.Model):
    class RelationType(models.TextChoices):
        OWES = "owes", "Owes"
        PAYS = "pays", "Pays"
        GUARANTEES = "guarantees", "Guarantees"
        LINKED_TO = "linked_to", "Linked To"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_edges")
    source = models.ForeignKey(CreditNode, on_delete=models.CASCADE, related_name="outgoing_edges")
    target = models.ForeignKey(CreditNode, on_delete=models.CASCADE, related_name="incoming_edges")
    relation_type = models.CharField(max_length=30, choices=RelationType.choices, db_index=True)
    weight = models.DecimalField(max_digits=8, decimal_places=4, default=1)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("source", "target", "relation_type")]
        indexes = [models.Index(fields=["user", "relation_type"])]
