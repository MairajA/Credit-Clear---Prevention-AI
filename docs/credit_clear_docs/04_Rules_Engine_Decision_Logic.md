# Credit Clear - Rules Engine & Decision Logic Document

**Version:** 1.0.0
**Last Updated:** April 2026
**Status:** In Development
**Confidential** - For Internal & Technical Review Only

---

## Table of Contents

1. [Overview](#1-overview)
2. [Rules Engine Architecture](#2-rules-engine-architecture)
3. [Risk Alert Rules](#3-risk-alert-rules)
4. [Intervention Decision Logic](#4-intervention-decision-logic)
5. [Fallback Payment Logic](#5-fallback-payment-logic)
6. [Credit Optimization Rules](#6-credit-optimization-rules)
7. [Fraud Detection Rules](#7-fraud-detection-rules)
8. [Notification Rules](#8-notification-rules)
9. [Gamification Rules](#9-gamification-rules)
10. [Recovery Roadmap Rules](#10-recovery-roadmap-rules)
11. [Business Rule Configuration](#11-business-rule-configuration)
12. [Rule Audit & Compliance](#12-rule-audit--compliance)

---

## 1. Overview

Credit Clear's decision-making is driven by a layered rules engine that combines deterministic business rules with AI model outputs. Rules are the guardrails that ensure the system behaves predictably, compliantly, and in the user's best interest.

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Transparency** | Every automated decision must have a traceable, human-readable reason |
| **User-First** | Rules always prioritize user financial wellbeing over platform metrics |
| **Fail-Safe** | If any rule evaluation fails, the system defaults to the safest action (usually: alert the user, do not act) |
| **Configurable** | Thresholds and parameters are configurable without code deployment |
| **Auditable** | All rule executions and outcomes are logged in `EventLog` |

### Rule Types

| Type | Description | Examples |
|------|-------------|---------|
| **Threshold Rules** | Numeric boundary triggers | Risk score >= 70% triggers alert |
| **State Machine Rules** | Status transition logic | Intervention: pending -> approved/denied |
| **Eligibility Rules** | Who qualifies for what | User eligible for credit builder if score < 650 |
| **Prioritization Rules** | Ordering and ranking | Which debt to negotiate first |
| **Compliance Rules** | Regulatory constraints | Max dispute frequency per bureau |
| **Business Rules** | Platform policies | Max fallback payment amount |

---

## 2. Rules Engine Architecture

```
+------------------+     +------------------+     +-------------------+
|                  |     |                  |     |                   |
|  Celery Beat     |---->|  Rule Evaluator  |---->|  Action Executor  |
|  (Scheduled)     |     |  (Python logic   |     |  (Celery Tasks)   |
|                  |     |   + DB config)   |     |                   |
+------------------+     +--------+---------+     +--------+----------+
                                  |                         |
                                  v                         v
                         +--------+---------+      +--------+----------+
                         |  EventLog        |      |  Model Tables     |
                         |  (Audit trail)   |      |  (State changes)  |
                         +------------------+      +-------------------+
```

### Evaluation Flow

```
1. TRIGGER: Celery Beat schedule OR API event OR webhook callback
2. CONTEXT: Load user data, account data, model scores
3. EVALUATE: Run applicable rules against context
4. DECIDE: Determine action(s) based on rule outcomes
5. EXECUTE: Dispatch Celery task(s) for chosen action(s)
6. LOG: Record rule evaluation + outcome in EventLog
7. NOTIFY: Send user notification if applicable
```

---

## 3. Risk Alert Rules

### 3.1 Risk Score Threshold Rule

```
RULE: RISK-001 — Trigger Risk Alert on High Probability

WHEN:
  RiskScoreSnapshot.missed_payment_probability >= threshold (default: 70.0)
  AND user has active linked accounts
  AND no open risk alert exists for the same payment due

THEN:
  1. Create RiskAlert with status = "open"
  2. Trigger Intervention Strategy Selection (RULE: INTV-001)
  3. Send notification to user (channel: push + in_app)
  4. Log event: "risk_alert.triggered"

PARAMETERS:
  - threshold: 70.0 (configurable per user tier)
  - cooldown_hours: 24 (don't re-alert for same payment within 24h)
```

### 3.2 Escalating Risk Rule

```
RULE: RISK-002 — Escalate Unresolved Risk

WHEN:
  RiskAlert.status == "open"
  AND RiskAlert.triggered_at > 48 hours ago
  AND no intervention has been executed

THEN:
  1. Escalate alert priority
  2. Retry intervention selection
  3. Send urgent notification (channel: sms + push)
  4. Flag for support agent review if 3rd escalation
  5. Log event: "risk_alert.escalated"
```

### 3.3 Risk Resolution Rule

```
RULE: RISK-003 — Auto-Resolve Risk Alert

WHEN:
  RiskAlert.status == "open"
  AND (
    associated PaymentDue.status == "paid"
    OR associated Intervention.status == "approved"
    OR RiskScoreSnapshot.missed_payment_probability < 40.0
  )

THEN:
  1. Update RiskAlert.status = "resolved"
  2. Set RiskAlert.resolved_at = now()
  3. Send resolution notification to user
  4. Award gamification points (RULE: GAM-002)
  5. Log event: "risk_alert.resolved"
```

---

## 4. Intervention Decision Logic

### 4.1 Strategy Selection Flow

```
RULE: INTV-001 — Select Intervention Strategy

INPUT: RiskAlert

STEP 1: Load creditor profile
  creditor = PaymentDue.creditor -> Creditor model
  IF creditor.is_active == False: GOTO STEP 5 (fallback)

STEP 2: Filter eligible strategies
  eligible = Creditor.supported_strategies
             INTERSECT Intervention.Strategy.choices
  IF eligible is empty: GOTO STEP 5 (fallback)

STEP 3: Rank strategies via AI model (or rule-based fallback)
  IF AI model available:
    ranked = StrategySelector.predict(context)
  ELSE:
    ranked = apply_default_ranking(eligible)

  DEFAULT RANKING (when AI unavailable):
    1. grace_period     (least invasive)
    2. due_date_change  (simple, high approval)
    3. extension        (moderate)
    4. installment      (requires creditor support)
    5. bnpl             (last resort before fallback)

STEP 4: Execute top strategy
  Create Intervention(strategy=ranked[0], status="pending")
  Dispatch Celery task: execute_creditor_api_call(intervention_id)

STEP 5: Fallback (no creditor or all strategies exhausted)
  Trigger Fallback Payment Logic (RULE: PAY-001)
```

### 4.2 Intervention Execution State Machine

```
                    +----------+
                    |  PENDING |
                    +-----+----+
                          |
              +-----------+-----------+
              |                       |
        +-----v------+        +------v-----+
        |  APPROVED  |        |   DENIED   |
        +-----+------+        +------+-----+
              |                       |
              v                       v
      Notify user &            Trigger fallback
      protect score            (RULE: PAY-001)
              |                       |
              v                       v
      Score simulation         Check if retry
      (avoided damage)         eligible (max 2)
                                      |
                               +------v------+
                               | If retries  |
                               | exhausted:  |
                               | FAILED      |
                               +-------------+
```

### 4.3 Intervention Retry Rule

```
RULE: INTV-002 — Retry Failed Intervention

WHEN:
  Intervention.status == "denied" OR "failed"
  AND retry_count < 2
  AND time_since_last_attempt > 4 hours

THEN:
  1. Select next-ranked strategy from INTV-001 results
  2. Create new Intervention with next strategy
  3. Execute via Celery task
  4. Log event: "intervention.retried"

MAX RETRIES: 2 (then escalate to fallback)
```

### 4.4 Creditor API Response Handling

```
RULE: INTV-003 — Handle Creditor API Response

CASE: HTTP 200 + approval in response body
  -> Intervention.status = "approved"
  -> Notify user
  -> Run score simulation
  -> Award gamification points

CASE: HTTP 200 + denial in response body
  -> Intervention.status = "denied"
  -> Trigger INTV-002 (retry) or PAY-001 (fallback)

CASE: HTTP 4xx (client error)
  -> Intervention.status = "failed"
  -> Log error details
  -> Retry with corrected payload if applicable

CASE: HTTP 5xx (server error) OR timeout
  -> Intervention.status = "pending" (keep open)
  -> Schedule retry in 1 hour (max 3 retries)
  -> If all retries fail: status = "failed", trigger fallback

ALL CASES:
  -> Create CreditorCommunicationLog entry
  -> Log event in EventLog
```

---

## 5. Fallback Payment Logic

### 5.1 Fallback Eligibility

```
RULE: PAY-001 — Initiate Fallback Payment

WHEN:
  Intervention.status == "denied"
  AND all retry attempts exhausted (INTV-002)
  AND PaymentDue.due_date <= today + 5 days
  AND user.fallback_payments(status="initiated").total_amount < MAX_FALLBACK_LIMIT

THEN:
  1. Calculate payment amount = PaymentDue.minimum_due (or amount_due if small)
  2. Determine payment method:
     IF amount <= $500: payment_method = "direct_pay"
     IF amount > $500 AND BNPL eligible: payment_method = "bnpl"
     ELSE: payment_method = "installment"
  3. Create FallbackPayment record
  4. Dispatch payment via payment provider
  5. Create RepaymentSchedule
  6. Notify user of fallback activation
  7. Log event: "fallback_payment.initiated"

PARAMETERS:
  - MAX_FALLBACK_LIMIT: $5,000 (per user, configurable)
  - MAX_ACTIVE_FALLBACKS: 3 (concurrent)
```

### 5.2 BNPL Activation Rule

```
RULE: PAY-002 — BNPL Provider Selection

WHEN:
  FallbackPayment.payment_method == "bnpl"

THEN:
  Select BNPL provider based on:
    1. Amount range (some providers have min/max)
    2. Best interest rate available
    3. Shortest approval time
    4. Provider availability

  Provider Priority:
    1. Affirm   (amounts $50-$17,500, 0-30% APR)
    2. Klarna   (amounts $35-$10,000, 0-24.99% APR)
    3. Afterpay (amounts $35-$2,000, 0% if on-time)

  Set FallbackPayment.bnpl_provider = selected
  Set FallbackPayment.interest_rate = provider_rate
  Set FallbackPayment.total_installments = provider_terms
```

### 5.3 Repayment Monitoring Rule

```
RULE: PAY-003 — Monitor Repayment Schedule

WHEN (daily check):
  RepaymentSchedule.status == "active"
  AND RepaymentSchedule.due_date <= today + 3 days

THEN:
  1. Send payment reminder notification
  2. IF due_date == today AND amount_paid < amount_due:
     -> Send urgent reminder
  3. IF due_date < today AND amount_paid < amount_due:
     -> Update status = "defaulted"
     -> Send warning notification
     -> Flag for collections follow-up
     -> Log event: "repayment.overdue"
```

---

## 6. Credit Optimization Rules

### 6.1 Auto-Dispute Generation

```
RULE: OPT-001 — Generate Dispute for Detected Error

WHEN:
  CreditAnalysis.detected_errors contains items
  AND error.confidence >= 0.85
  AND no existing BureauDispute for same account + bureau + error_type

THEN:
  1. Create OptimizationCase(case_type="credit_repair")
  2. For each bureau reporting the error:
     a. Create BureauDispute(status="draft")
     b. Generate dispute letter from template
     c. Attach evidence (if available from Plaid data)
  3. Queue for review (auto-submit if confidence >= 0.95)
  4. Notify user of pending disputes
  5. Log event: "dispute.auto_generated"

COMPLIANCE CONSTRAINTS:
  - Max 5 disputes per bureau per 30-day period
  - Wait 30 days between disputes for same item
  - User must have verified identity before filing
```

### 6.2 Dispute Escalation Rule

```
RULE: OPT-002 — Escalate Unresolved Dispute

WHEN:
  BureauDispute.status == "submitted"
  AND submitted_at > 30 days ago
  AND no response received

THEN:
  1. Update status = "escalated"
  2. File CFPB complaint (generate complaint from dispute details)
  3. Set BureauDispute.cfpb_complaint_id
  4. Notify user of escalation
  5. Log event: "dispute.escalated_to_cfpb"

WHEN:
  BureauDispute.status == "responded"
  AND bureau_response indicates "verified" (not removed)
  AND evidence strongly supports dispute (confidence >= 0.90)

THEN:
  1. Option A: Re-submit with additional evidence
  2. Option B: Escalate to CFPB
  3. Notify user with options
```

### 6.3 Debt Negotiation Prioritization

```
RULE: OPT-003 — Prioritize Debts for Negotiation

SCORE each debt:
  priority_score = (
    (impact_on_credit_score * 0.30)      # Higher impact = higher priority
    + (settlement_likelihood * 0.25)      # More likely to settle = higher
    + (account_age_factor * 0.20)         # Older debts = easier to settle
    + (amount_factor * 0.15)              # Larger savings potential = higher
    + (urgency_factor * 0.10)             # Approaching statute of limitations
  )

RANKING:
  1. Collections accounts (highest settlement potential)
  2. Charged-off accounts
  3. High-interest credit card balances
  4. Medical debt (often negotiable)
  5. Current accounts with high interest (rate reduction)

CONSTRAINTS:
  - Max 3 active negotiations simultaneously
  - Wait 14 days between offers to same creditor
  - Do not negotiate accounts in active dispute
```

### 6.4 Credit Building Eligibility

```
RULE: OPT-004 — Recommend Credit Building Products

WHEN:
  User credit_score < 650
  AND User has no active credit_building OptimizationCase

THEN recommend based on score tier:

  SCORE 300-499 (Very Poor):
    1. Secured credit card (deposit required)
    2. Credit builder loan
    3. Rent reporting service

  SCORE 500-579 (Poor):
    1. Secured credit card
    2. Credit builder loan
    3. Authorized tradeline (if family available)

  SCORE 580-649 (Fair):
    1. Student/starter unsecured card
    2. Rent reporting
    3. Authorized tradeline

  FOR ALL:
    - Check if product reports to all 3 bureaus (prefer tri-bureau reporting)
    - Prefer lowest fee options
    - Create CreditBuildingProduct entries with status="recommended"
```

### 6.5 Bill Negotiation Triggers

```
RULE: OPT-005 — Identify Negotiable Bills

WHEN (monthly scan):
  User has linked accounts with recurring charges

CHECK each category:
  1. MEDICAL: Any medical bill > $500
     -> Recommend hardship program or settlement
  2. CREDIT CARD INTEREST: Any card with APR > 20% AND balance > $1,000
     -> Recommend interest rate reduction call
  3. SUBSCRIPTIONS: Identify unused subscriptions (no merchant activity in 60 days)
     -> Recommend cancellation
  4. INSURANCE: Annual premium renewal approaching
     -> Recommend rate comparison
  5. COLLECTIONS: Any new collection account
     -> Recommend pay-for-delete negotiation

THEN:
  Create BillNegotiationResult entries for each actionable item
  Notify user with savings estimates
```

---

## 7. Fraud Detection Rules

### 7.1 Rule Definitions

```
RULE: FRD-001 — New Account Alert
WHEN: Bureau report shows new account not in user's LinkedAccounts
SEVERITY: HIGH
ACTION: Create FraudAlert, notify immediately, offer one-click dispute

RULE: FRD-002 — Unauthorized Hard Inquiry
WHEN: Bureau report shows hard inquiry, user did not initiate
SEVERITY: MEDIUM
ACTION: Create FraudAlert, notify user, offer dispute

RULE: FRD-003 — Dark Web Data Exposure
WHEN: Dark web scan finds user email, phone, or SSN
SEVERITY: CRITICAL (SSN) / MEDIUM (email/phone)
ACTION: Create FraudAlert, recommend password changes / credit freeze

RULE: FRD-004 — Address Change Not By User
WHEN: Bureau shows address change, user did not update
SEVERITY: HIGH
ACTION: Create FraudAlert, recommend identity verification

RULE: FRD-005 — Rapid Account Opening
WHEN: 3+ new accounts opened in 30 days
SEVERITY: HIGH
ACTION: Create FraudAlert, recommend credit freeze

RULE: FRD-006 — Unusual Balance Spike
WHEN: Account balance increases > 50% in 7 days (not from payment)
SEVERITY: MEDIUM
ACTION: Create FraudAlert, ask user to verify

RULE: FRD-007 — Collection Account Mismatch
WHEN: New collection appears, no corresponding original account
SEVERITY: HIGH
ACTION: Create FraudAlert, auto-generate dispute
```

### 7.2 Auto-Response Rules

```
RULE: FRD-AUTO-001 — Auto-File Fraud Dispute

WHEN:
  FraudAlert.severity == "critical"
  AND FraudAlert.alert_type IN ("new_account", "identity_theft")
  AND user has fraud_auto_dispute_enabled == True

THEN:
  1. Create BureauDispute for all 3 bureaus
  2. Set dispute_reason = "Identity theft - unauthorized account"
  3. Set FraudAlert.auto_dispute_filed = True
  4. Notify user of auto-action taken
```

---

## 8. Notification Rules

### 8.1 Notification Dispatch Logic

```
RULE: NOTIF-001 — Send Notification

INPUT: event_type, user_id, payload

STEP 1: Check NotificationPreference for user
  preferences = user.notification_preferences

STEP 2: Determine channels
  channels = []
  FOR each channel in [in_app, push, email, sms]:
    IF preferences.{channel}.is_enabled
       AND preferences.{channel}.{event_category} == True
       AND NOT in quiet_hours(channel):
      channels.append(channel)

STEP 3: Priority override
  IF event_type.severity == "critical":
    channels = [in_app, push, sms]  # Always send critical alerts
    IGNORE quiet_hours

STEP 4: Dispatch
  FOR each channel in channels:
    Create Notification(channel, status="queued")
    Dispatch via Celery task
```

### 8.2 Notification Event Categories

| Event | Category Field | Default Channels | Priority |
|-------|---------------|-----------------|----------|
| Risk alert triggered | `risk_alerts` | push, in_app | HIGH |
| Intervention approved | `intervention_updates` | push, in_app, email | MEDIUM |
| Intervention denied | `intervention_updates` | push, in_app, sms | HIGH |
| Payment due reminder (3 days) | `payment_reminders` | push, in_app | MEDIUM |
| Payment due reminder (1 day) | `payment_reminders` | push, in_app, sms | HIGH |
| Payment overdue | `payment_reminders` | push, in_app, sms, email | CRITICAL |
| Score change detected | `score_changes` | push, in_app | LOW |
| Fraud alert | `fraud_alerts` | push, in_app, sms, email | CRITICAL |
| Dispute status update | `intervention_updates` | in_app, email | LOW |
| Weekly summary | `weekly_summary` | email | LOW |

### 8.3 Quiet Hours Rule

```
RULE: NOTIF-002 — Quiet Hours

WHEN:
  NotificationPreference.quiet_hours_start is set
  AND current_time BETWEEN quiet_hours_start AND quiet_hours_end

THEN:
  - LOW/MEDIUM priority: Queue and send after quiet hours end
  - HIGH priority: Queue and send after quiet hours end
  - CRITICAL priority: Send immediately (override quiet hours)
```

---

## 9. Gamification Rules

### 9.1 Points Earning Rules

```
RULE: GAM-001 — Award Points for Actions

| Action | Points | Source | Conditions |
|--------|--------|--------|------------|
| Link first bank account | 100 | account_linked | First account only |
| Link additional account | 25 | account_linked | Subsequent accounts |
| Complete onboarding | 200 | milestone | All setup steps done |
| On-time payment recorded | 50 | payment_on_time | Per payment |
| 30-day on-time streak | 150 | streak_bonus | All payments on time |
| 90-day on-time streak | 500 | streak_bonus | All payments on time |
| Dispute filed | 75 | dispute_filed | Per dispute |
| Dispute resolved (success) | 200 | dispute_filed | Error removed |
| Credit score improved | 100 | score_improved | Per 10-point improvement |
| Course completed | 50 | course_completed | Per education module |
| Referred a friend | 300 | referral | Per successful referral |
```

### 9.2 Level Progression Rule

```
RULE: GAM-002 — Level Calculation

Level thresholds:
  Level 1:  0 - 499 points       (Beginner)
  Level 2:  500 - 1,499 points   (Builder)
  Level 3:  1,500 - 3,499 points (Protector)
  Level 4:  3,500 - 6,999 points (Champion)
  Level 5:  7,000+ points        (Credit Master)

WHEN:
  UserReward created (new points)

THEN:
  1. Update UserPointsBalance.total_points += points_delta
  2. Recalculate level based on thresholds
  3. IF level changed:
     a. Award level-up badge
     b. Send celebration notification
     c. Log event: "gamification.level_up"
```

### 9.3 Streak Tracking Rule

```
RULE: GAM-003 — Daily Streak

WHEN (daily check):
  User performed qualifying action today
  (login, payment, dispute follow-up, course progress)

THEN:
  1. UserPointsBalance.streak_days += 1
  2. IF streak_days > longest_streak:
     Update longest_streak
  3. Award streak milestone badges:
     - 7 days: "Week Warrior" badge + 50 pts
     - 30 days: "Monthly Master" badge + 200 pts
     - 90 days: "Quarter Champion" badge + 500 pts

WHEN:
  User has no qualifying action for 24 hours

THEN:
  1. Reset UserPointsBalance.streak_days = 0
  2. Send encouragement notification
```

---

## 10. Recovery Roadmap Rules

### 10.1 Milestone Activation Rule

```
RULE: ROAD-001 — Activate Next Milestone

WHEN:
  RoadmapMilestone(month_index=N).status == "completed"
  AND RoadmapMilestone(month_index=N+1).status == "pending"

THEN:
  1. Set milestone(N+1).status = "active"
  2. Set milestone(N+1).started_at = now()
  3. Notify user of new milestone unlock
  4. Log event: "roadmap.milestone_activated"
```

### 10.2 Action Completion Tracking Rule

```
RULE: ROAD-002 — Track Action Completion

WHEN:
  RoadmapAction links to an optimization case or dispute
  AND linked entity reaches terminal state (completed/resolved)

THEN:
  1. Update RoadmapAction.status = "completed"
  2. Set RoadmapAction.completed_at = now()
  3. Check if all actions in milestone are complete
     IF yes: complete milestone (ROAD-001 triggers next)
  4. Award gamification points
  5. Log event: "roadmap.action_completed"
```

### 10.3 Roadmap Adaptation Rule

```
RULE: ROAD-003 — Adapt Roadmap Based on Progress

WHEN (weekly evaluation):
  User credit_score has changed significantly (>= 20 points)
  OR New issues discovered in latest CreditAnalysis
  OR User completed actions ahead of schedule

THEN:
  1. Re-evaluate remaining milestones
  2. Add new actions for newly discovered issues
  3. Remove actions that are no longer relevant
  4. Adjust estimated_score_impact based on updated data
  5. Notify user of roadmap updates
```

---

## 11. Business Rule Configuration

### 11.1 Configurable Parameters

All threshold values are stored as system configuration (database or environment), not hardcoded:

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| `RISK_SCORE_THRESHOLD` | 70.0 | DB Config | MPPS threshold for alert trigger |
| `RISK_ALERT_COOLDOWN_HOURS` | 24 | DB Config | Min hours between alerts for same payment |
| `MAX_INTERVENTION_RETRIES` | 2 | DB Config | Max retry attempts per intervention |
| `MAX_FALLBACK_AMOUNT` | 5000.00 | DB Config | Max fallback payment per user |
| `MAX_ACTIVE_FALLBACKS` | 3 | DB Config | Max concurrent fallback payments |
| `MAX_DISPUTES_PER_BUREAU_30D` | 5 | DB Config | Dispute rate limit per bureau |
| `AUTO_DISPUTE_CONFIDENCE` | 0.95 | DB Config | Auto-submit dispute confidence threshold |
| `MAX_ACTIVE_NEGOTIATIONS` | 3 | DB Config | Concurrent negotiation limit |
| `STREAK_RESET_HOURS` | 24 | DB Config | Hours of inactivity to reset streak |
| `BNPL_AMOUNT_THRESHOLD` | 500.00 | DB Config | Amount above which BNPL is preferred |

### 11.2 Rule Priority Order

When multiple rules fire simultaneously, execution order:

```
Priority 1 (CRITICAL): Fraud detection rules (FRD-*)
Priority 2 (HIGH):     Risk alert rules (RISK-*)
Priority 3 (HIGH):     Intervention rules (INTV-*)
Priority 4 (MEDIUM):   Payment rules (PAY-*)
Priority 5 (MEDIUM):   Optimization rules (OPT-*)
Priority 6 (LOW):      Notification rules (NOTIF-*)
Priority 7 (LOW):      Gamification rules (GAM-*)
Priority 8 (LOW):      Roadmap rules (ROAD-*)
```

---

## 12. Rule Audit & Compliance

### 12.1 Audit Trail

Every rule execution produces an `EventLog` entry:

```json
{
  "event_name": "rule.executed",
  "event_source": "rules_engine",
  "metadata": {
    "rule_id": "RISK-001",
    "rule_name": "Trigger Risk Alert on High Probability",
    "input": {
      "user_id": 12345,
      "probability": 78.5,
      "threshold": 70.0
    },
    "outcome": "alert_triggered",
    "actions_taken": ["risk_alert.created", "intervention.initiated", "notification.queued"],
    "execution_time_ms": 45
  },
  "occurred_at": "2026-04-10T08:00:00Z"
}
```

### 12.2 Compliance Requirements

| Regulation | Requirement | Implementation |
|-----------|-------------|----------------|
| **FCRA** | Disputes must be investigated within 30 days | OPT-002 escalation rule |
| **FCRA** | Users can dispute inaccurate information | OPT-001 auto-dispute |
| **ECOA** | No discrimination in credit decisions | Bias testing on all models |
| **CFPB** | Consumers can file complaints | OPT-002 CFPB escalation |
| **TCPA** | SMS requires opt-in consent | NOTIF-001 preference check |
| **CAN-SPAM** | Marketing email opt-out | NotificationPreference.marketing |
| **State Laws** | Debt collection communication limits | OPT-003 negotiation frequency limits |

### 12.3 Rule Change Management

| Step | Description | Responsible |
|------|-------------|-------------|
| 1 | Propose rule change with business justification | Product / Compliance |
| 2 | Review impact analysis (which users affected) | Engineering + Risk |
| 3 | Implement in staging with A/B test | Engineering |
| 4 | Compliance review | Legal / Compliance |
| 5 | Gradual rollout (10% -> 50% -> 100%) | Engineering |
| 6 | Monitor metrics for 7 days | Data / Risk |
| 7 | Document change in rule change log | All |

---

*Rules and thresholds subject to refinement during active development and compliance review.*
