# Credit Clear - AI / ML Model Design Document

**Version:** 1.0.0
**Last Updated:** April 2026
**Status:** In Development
**Confidential** - For Internal & Technical Review Only

---

## Table of Contents

1. [Overview](#1-overview)
2. [AI System Architecture](#2-ai-system-architecture)
3. [Model 1: Missed Payment Probability Score (MPPS)](#3-model-1-missed-payment-probability-score-mpps)
4. [Model 2: Credit Report Analysis Engine](#4-model-2-credit-report-analysis-engine)
5. [Model 3: Intervention Strategy Selector](#5-model-3-intervention-strategy-selector)
6. [Model 4: Score Simulator & Forecaster](#6-model-4-score-simulator--forecaster)
7. [Model 5: Debt Negotiation AI](#7-model-5-debt-negotiation-ai)
8. [Model 6: Recovery Plan Generator](#8-model-6-recovery-plan-generator)
9. [Model 7: Fraud Detection Engine](#9-model-7-fraud-detection-engine)
10. [Model Performance & Monitoring](#10-model-performance--monitoring)
11. [Data Pipeline Architecture](#11-data-pipeline-architecture)
12. [Model Versioning & Deployment](#12-model-versioning--deployment)

---

## 1. Overview

Credit Clear employs a suite of AI/ML models that work together to deliver predictive credit protection. The AI system operates across three layers:

| Layer | Function | Models |
|-------|----------|--------|
| **Prediction** | Anticipate risks before they happen | MPPS, Fraud Detection |
| **Decision** | Choose optimal actions automatically | Strategy Selector, Negotiation AI |
| **Generation** | Create personalized plans and analyses | Report Analysis, Recovery Plan, Score Simulator |

### Design Principles

1. **Explainability** - Every AI decision must produce human-readable reasoning
2. **Auditability** - All model inputs, outputs, and versions are logged
3. **Fairness** - Models are tested for demographic bias and comply with ECOA/FCRA
4. **Fail-safe** - Model failures fall back to rule-based defaults, never to inaction

---

## 2. AI System Architecture

```
+-------------------------------------------------------------------+
|                        DATA INGESTION LAYER                        |
|  +-------------+  +------------+  +------------+  +-------------+ |
|  | Plaid Sync  |  | Bureau     |  | Creditor   |  | User        | |
|  | (Accounts,  |  | Reports    |  | Responses  |  | Behavior    | |
|  | Transactions)|  | (3 Bureau) |  | (API Logs) |  | (App Usage) | |
|  +------+------+  +-----+------+  +-----+------+  +------+------+ |
|         |               |               |                |         |
+---------+---------------+---------------+----------------+---------+
          |               |               |                |
+---------v---------------v---------------v----------------v---------+
|                     FEATURE ENGINEERING LAYER                       |
|  +-------------------+  +------------------+  +------------------+ |
|  | Financial         |  | Credit Profile   |  | Behavioral       | |
|  | Features          |  | Features         |  | Features         | |
|  | - balance_trend   |  | - utilization    |  | - login_freq     | |
|  | - income_pattern  |  | - derog_count    |  | - alert_response | |
|  | - expense_ratio   |  | - age_of_credit  |  | - payment_habit  | |
|  | - recurring_bills |  | - inquiry_count  |  | - engagement     | |
|  +--------+----------+  +--------+---------+  +--------+---------+ |
|           |                      |                      |          |
+-----------+----------------------+----------------------+----------+
            |                      |                      |
+-----------v----------------------v----------------------v----------+
|                        MODEL INFERENCE LAYER                       |
|                                                                    |
|  +--------+  +----------+  +----------+  +---------+  +---------+ |
|  |  MPPS  |  | Strategy |  | Score    |  | Report  |  | Fraud   | |
|  | Model  |  | Selector |  | Forecast |  | Analyzer|  | Detect  | |
|  +---+----+  +----+-----+  +----+-----+  +----+----+  +----+----+ |
|      |            |              |              |            |      |
+------+------------+--------------+--------------+------------+-----+
       |            |              |              |            |
+------v------------v--------------v--------------v------------v-----+
|                       ACTION & STORAGE LAYER                       |
|                                                                    |
|  RiskScoreSnapshot | Intervention | ScoreSimulation | CreditAnalysis|
|  RiskAlert         | FallbackPay  | RecoveryPlan    | FraudAlert    |
+-------------------------------------------------------------------+
```

---

## 3. Model 1: Missed Payment Probability Score (MPPS)

### 3.1 Purpose
Predict the probability (0-100%) that a user will miss an upcoming payment within the next 14 days. This is the core prevention engine that triggers the entire intervention flow.

### 3.2 Model Specification

| Attribute | Detail |
|-----------|--------|
| **Type** | Gradient Boosted Decision Tree (XGBoost / LightGBM) |
| **Output** | Probability score (0.00 - 100.00) |
| **Threshold** | 70% triggers risk alert and intervention |
| **Frequency** | Daily per user (Celery Beat scheduled) |
| **Latency Target** | < 500ms per user |
| **Stored In** | `RiskScoreSnapshot` |

### 3.3 Feature Set

| # | Feature Name | Source | Type | Description |
|---|-------------|--------|------|-------------|
| 1 | `days_until_due` | `PaymentDue` | Numeric | Days until next payment due date |
| 2 | `current_balance` | `LinkedAccount` | Numeric | Current account balance |
| 3 | `available_balance` | `LinkedAccount` | Numeric | Available spending balance |
| 4 | `balance_to_due_ratio` | Computed | Numeric | `available_balance / amount_due` |
| 5 | `avg_monthly_income` | `Transaction` (30d) | Numeric | Average monthly inflow |
| 6 | `avg_monthly_expenses` | `Transaction` (30d) | Numeric | Average monthly outflow |
| 7 | `income_expense_ratio` | Computed | Numeric | Income vs expenses ratio |
| 8 | `days_since_last_income` | `Transaction` | Numeric | Days since last income deposit |
| 9 | `expected_income_in` | Pattern analysis | Numeric | Expected days until next income |
| 10 | `recurring_bill_count` | `Transaction` | Numeric | Number of recurring obligations |
| 11 | `total_upcoming_dues_7d` | `PaymentDue` | Numeric | Total due in next 7 days |
| 12 | `total_upcoming_dues_14d` | `PaymentDue` | Numeric | Total due in next 14 days |
| 13 | `missed_payments_3m` | `PaymentDue` | Numeric | Missed payments in last 90 days |
| 14 | `missed_payments_12m` | `PaymentDue` | Numeric | Missed payments in last 12 months |
| 15 | `auto_pay_enabled` | `PaymentDue` | Boolean | Is auto-pay set up? |
| 16 | `credit_utilization` | `CreditReportPull` | Numeric | Current credit utilization % |
| 17 | `balance_trend_7d` | `Transaction` | Numeric | Balance change direction (7 day) |
| 18 | `balance_trend_30d` | `Transaction` | Numeric | Balance change direction (30 day) |
| 19 | `unusual_expense_flag` | Pattern analysis | Boolean | Unusual spending spike detected |
| 20 | `account_type` | `LinkedAccount` | Categorical | Bank / Card / Loan / Biller |

### 3.4 Training Strategy

| Aspect | Detail |
|--------|--------|
| **Training Data** | Historical payment outcomes (on-time vs missed) |
| **Label** | Binary: 1 = payment missed within 14 days, 0 = paid on time |
| **Validation** | 5-fold time-series cross-validation |
| **Metrics** | AUC-ROC (primary), Precision@70 threshold, Recall, F1 |
| **Target AUC** | >= 0.85 |
| **Retraining** | Monthly, triggered by performance drift or new data volume |
| **Bias Testing** | Tested across age, income, and geographic segments |

### 3.5 Output Schema

```json
{
  "user_id": 12345,
  "account_id": 678,
  "missed_payment_probability": 78.5,
  "threshold": 70.0,
  "alert_triggered": true,
  "score_factors": {
    "low_balance": 0.35,
    "high_upcoming_dues": 0.25,
    "missed_history": 0.20,
    "income_timing": 0.15,
    "spending_spike": 0.05
  },
  "model_version": "mpps-v1.2.0",
  "evaluated_at": "2026-04-10T08:00:00Z"
}
```

---

## 4. Model 2: Credit Report Analysis Engine

### 4.1 Purpose
Analyze raw credit bureau reports, identify errors, find improvement opportunities, and estimate potential score gains.

### 4.2 Model Specification

| Attribute | Detail |
|-----------|--------|
| **Type** | Rule-based analysis + NLP (for narrative fields) + ML classifier (for error detection) |
| **Input** | Raw credit report JSON from `CreditReportPull.raw_report` |
| **Output** | Structured analysis stored in `CreditAnalysis` |
| **Trigger** | After each successful credit report pull |
| **Stored In** | `CreditAnalysis` |

### 4.3 Analysis Components

#### A. Error Detection Module

| Error Type | Detection Method | Disputability |
|-----------|-----------------|---------------|
| Incorrect personal info | Rule-based matching against verified identity | High |
| Duplicate accounts | Fuzzy matching on account number, creditor, balance | High |
| Incorrect balance | Compare bureau balance vs actual account balance (Plaid) | High |
| Wrong payment status | Compare reported status vs transaction history | High |
| Outdated negative items | Age-based rules (7-year rule for derogatory marks) | High |
| Unauthorized hard inquiries | User verification of each inquiry | Medium |
| Mixed file (wrong person) | Identity mismatch detection | High |
| Incorrect account ownership | Authorized user vs primary borrower rules | Medium |

#### B. Improvement Opportunity Detection

| Opportunity | Algorithm | Potential Impact |
|------------|-----------|-----------------|
| High utilization accounts | Threshold analysis (> 30% utilization) | 20-50 points |
| Authorized tradeline opportunities | Score simulation | 10-30 points |
| Dispute-removable negatives | Error classification model | 20-100 points |
| Balance paydown sequencing | Optimization algorithm (highest util first) | 15-40 points |
| Credit mix improvement | Gap analysis (installment vs revolving) | 5-15 points |
| Age of credit optimization | Oldest account analysis | 5-10 points |

#### C. Output Schema

```json
{
  "user_id": 12345,
  "bureau_source": "experian",
  "credit_score": 625,
  "risk_summary": "Below average credit with 3 disputable errors and high utilization on 2 accounts.",
  "detected_errors": [
    {
      "type": "incorrect_balance",
      "account": "Chase Visa ****1234",
      "reported": 5200.00,
      "actual": 3100.00,
      "confidence": 0.92,
      "recommended_action": "file_dispute"
    }
  ],
  "improvement_opportunities": [
    {
      "type": "reduce_utilization",
      "account": "Discover ****5678",
      "current_utilization": 85,
      "target_utilization": 30,
      "estimated_score_gain": 25,
      "recommended_action": "pay_down_balance"
    }
  ],
  "estimated_score_gain": 45,
  "model_version": "cra-v2.1.0"
}
```

---

## 5. Model 3: Intervention Strategy Selector

### 5.1 Purpose
When a risk alert fires, automatically select the optimal intervention strategy based on the creditor, account type, user history, and likelihood of approval.

### 5.2 Model Specification

| Attribute | Detail |
|-----------|--------|
| **Type** | Multi-Armed Bandit (Thompson Sampling) with fallback to Decision Tree |
| **Input** | Risk alert context, creditor profile, user history |
| **Output** | Ranked list of strategies with approval probability |
| **Stored In** | `Intervention.strategy` |

### 5.3 Strategy Selection Features

| Feature | Source | Description |
|---------|--------|-------------|
| `creditor_slug` | `Creditor` | Which creditor we're dealing with |
| `creditor_success_rate` | `Creditor` | Historical success rate |
| `supported_strategies` | `Creditor` | Which strategies creditor accepts |
| `account_type` | `LinkedAccount` | Bank / Card / Loan / Biller |
| `days_until_due` | `PaymentDue` | Urgency level |
| `amount_due` | `PaymentDue` | Payment amount |
| `user_tenure_months` | `User` | How long user has been with creditor |
| `past_interventions_count` | `Intervention` | Previous interventions with this creditor |
| `past_intervention_outcomes` | `Intervention` | Success/failure history |
| `user_credit_score` | `CreditReportPull` | Current credit score |
| `payment_history_12m` | `PaymentDue` | On-time payment rate |

### 5.4 Strategy Ranking Output

```json
{
  "risk_alert_id": 456,
  "recommended_strategies": [
    {
      "strategy": "grace_period",
      "approval_probability": 0.85,
      "creditor_supports": true,
      "reasoning": "Creditor has 85% approval rate for grace periods; user has clean 12-month history."
    },
    {
      "strategy": "extension",
      "approval_probability": 0.72,
      "creditor_supports": true,
      "reasoning": "Extension supported but lower approval rate for this creditor category."
    },
    {
      "strategy": "bnpl",
      "approval_probability": 0.95,
      "creditor_supports": false,
      "reasoning": "Fallback option: BNPL via Credit Clear if creditor denies direct intervention."
    }
  ],
  "selected_strategy": "grace_period",
  "model_version": "iss-v1.0.0"
}
```

### 5.5 Learning Loop

```
Intervention Executed --> Creditor Response (Approved/Denied)
        |                           |
        v                           v
  Update Bandit Model        Log outcome in
  (reward = approved,        CreditorCommunicationLog
   penalty = denied)
        |
        v
  Improved strategy selection for next intervention
```

---

## 6. Model 4: Score Simulator & Forecaster

### 6.1 Purpose
Predict the impact of specific actions on a user's credit score, allowing users to see the value of interventions and plan future actions.

### 6.2 Model Specification

| Attribute | Detail |
|-----------|--------|
| **Type** | Ensemble: Credit score regression model + VantageScore factor simulation |
| **Simulation Types** | `intervention` (impact of action), `what_if` (scenario), `forecast` (time-based) |
| **Output** | Current, projected, best-case, worst-case scores + factor breakdown |
| **Stored In** | `ScoreSimulation` |

### 6.3 Simulation Scenarios

| Scenario | Input Parameters | Output |
|----------|-----------------|--------|
| "What if I pay down Card X to 30%?" | Account, target balance | Projected score change |
| "What if this dispute gets removed?" | Dispute type, account | Projected score change |
| "What if I miss this payment?" | Account, payment amount | Damage estimate |
| "Score forecast next 90 days" | Current trajectory | Month-by-month projection |
| "Impact of Credit Clear intervention" | Intervention details | Damage avoided |

### 6.4 Score Factor Weights (VantageScore Model)

| Factor | Weight | Features |
|--------|--------|----------|
| Payment History | 40% | On-time %, missed count, recency |
| Credit Utilization | 20% | Overall utilization, per-card utilization |
| Age of Credit | 21% | Average age, oldest account |
| Credit Mix | 11% | Types of accounts (revolving, installment, mortgage) |
| Recent Inquiries | 5% | Hard inquiry count in 24 months |
| Available Credit | 3% | Total available credit, new accounts |

### 6.5 Output Schema

```json
{
  "simulation_type": "intervention",
  "current_score": 625,
  "projected_score": 648,
  "best_case_score": 660,
  "worst_case_score": 625,
  "avoided_damage_points": 35,
  "score_factors_breakdown": {
    "payment_history": "+15 (missed payment prevented)",
    "utilization": "+8 (will remain stable)",
    "credit_age": "0 (no change)",
    "credit_mix": "0 (no change)",
    "inquiries": "0 (no new inquiry)"
  },
  "recommended_actions": [
    "Pay Discover card below 30% utilization for additional +25 points",
    "File dispute on incorrect Chase balance for potential +15 points"
  ],
  "horizon_days": 90,
  "model_version": "ss-v1.3.0"
}
```

---

## 7. Model 5: Debt Negotiation AI

### 7.1 Purpose
Automate debt negotiation by analyzing account details, creditor patterns, and optimal offer strategies to maximize savings.

### 7.2 Model Specification

| Attribute | Detail |
|-----------|--------|
| **Type** | Reinforcement Learning agent (negotiation turns) + Statistical model (offer pricing) |
| **Input** | Debt amount, creditor, account age, payment history |
| **Output** | Optimal offer amount, negotiation strategy, communication templates |
| **Stored In** | `NegotiationOffer`, `SettlementAgreement` |

### 7.3 Negotiation Strategy Matrix

| Account Status | Debt Age | Recommended Strategy | Typical Settlement Range |
|---------------|----------|---------------------|------------------------|
| Current (no missed) | Any | Interest Rate Reduction | 2-8% APR reduction |
| 30-60 days late | < 6 months | Payment Plan | 100% balance, extended terms |
| 90-120 days late | 6-12 months | Settlement Offer | 40-60% of balance |
| Charged Off | 12-24 months | Settlement / Pay-for-Delete | 25-50% of balance |
| In Collections | > 24 months | Settlement / Pay-for-Delete | 15-40% of balance |
| Medical Debt | Any | Settlement + Hardship | 20-50% of balance |

### 7.4 Offer Optimization Algorithm

```
Input: original_balance, creditor_type, account_age, user_hardship_level

Step 1: Determine settlement floor based on historical data
        floor = creditor_category_avg_settlement_rate * original_balance

Step 2: Calculate initial offer
        initial_offer = floor * 0.70  (start 30% below expected)

Step 3: Set negotiation ceiling
        ceiling = floor * 1.15  (max 15% above floor)

Step 4: Generate counter-offer responses
        For each creditor counter:
          if counter <= ceiling: ACCEPT
          if counter > ceiling: counter_with (ceiling - offset)
          max_rounds: 3

Output: NegotiationOffer with offer_type, offered_amount, communication_log
```

---

## 8. Model 6: Recovery Plan Generator

### 8.1 Purpose
Generate personalized 90-day credit recovery plans by analyzing the user's credit profile and selecting the optimal sequence of actions.

### 8.2 Model Specification

| Attribute | Detail |
|-----------|--------|
| **Type** | Optimization algorithm (constrained scheduling) + Template-based generation |
| **Input** | `CreditAnalysis`, `CreditReportPull`, user goals |
| **Output** | Month-by-month milestones with ordered actions |
| **Stored In** | `RecoveryPlan`, `RoadmapMilestone`, `RoadmapAction` |

### 8.3 Recovery Plan Template (90 Days)

| Month | Priority Actions | Expected Impact |
|-------|-----------------|----------------|
| **Month 1** (Days 1-30) | File disputes for detected errors; Set up payment reminders; Link all accounts | Remove inaccurate negatives; Establish baseline |
| **Month 2** (Days 31-60) | Pay down highest utilization accounts; Apply for credit builder if applicable; Begin debt negotiation | Reduce utilization below 30%; Diversify credit mix |
| **Month 3** (Days 61-90) | Follow up on disputes; Open authorized tradeline if eligible; Review and optimize recurring bills | Maximize score improvement; Sustain gains |

### 8.4 Action Prioritization Algorithm

```
For each potential action:
  score = (estimated_score_impact * 0.4)
        + (ease_of_execution * 0.3)
        + (time_sensitivity * 0.2)
        + (cost_to_user * 0.1)  # lower cost = higher score

Sort actions by score descending
Assign to milestones based on dependencies and timing constraints
```

---

## 9. Model 7: Fraud Detection Engine

### 9.1 Purpose
Detect identity theft, unauthorized accounts, and suspicious activity across the user's credit profile and linked accounts.

### 9.2 Model Specification

| Attribute | Detail |
|-----------|--------|
| **Type** | Anomaly detection (Isolation Forest) + Rule-based alerts |
| **Input** | Bureau data, transaction patterns, dark web scan results |
| **Output** | Fraud alerts with severity and recommended actions |
| **Stored In** | `FraudAlert` |

### 9.3 Detection Rules

| Rule ID | Trigger | Severity | Auto-Action |
|---------|---------|----------|-------------|
| FR-001 | New account opened not recognized by user | HIGH | Freeze alert + dispute |
| FR-002 | Hard inquiry not initiated by user | MEDIUM | Notify user + offer dispute |
| FR-003 | Address change on bureau not initiated by user | HIGH | Identity verification alert |
| FR-004 | Email/phone found on dark web breach | MEDIUM | Password change recommendation |
| FR-005 | SSN found on dark web | CRITICAL | Full identity lock recommendation |
| FR-006 | Unusual transaction pattern (amount/frequency) | MEDIUM | Transaction review alert |
| FR-007 | Multiple new accounts in short period | HIGH | Possible identity theft alert |
| FR-008 | Balance spike on unknown account | HIGH | Account verification alert |

### 9.4 Anomaly Detection Features

| Feature | Normal Range | Alert Threshold |
|---------|-------------|----------------|
| New accounts per month | 0-1 | >= 3 |
| Hard inquiries per month | 0-2 | >= 4 |
| Balance increase rate (%) | 0-10% | >= 50% |
| New creditor count per week | 0 | >= 2 |
| Address changes per year | 0-1 | >= 3 |

---

## 10. Model Performance & Monitoring

### 10.1 Performance Tracking

All model performance is tracked via the `ModelPerformanceMetric` model:

```json
{
  "metric_name": "auc_roc",
  "model_version": "mpps-v1.2.0",
  "metric_value": 0.8723,
  "evaluated_at": "2026-04-10T00:00:00Z",
  "context": {
    "dataset_size": 50000,
    "evaluation_type": "weekly_backtest"
  }
}
```

### 10.2 Key Performance Indicators

| Model | Primary Metric | Target | Alert Threshold |
|-------|---------------|--------|----------------|
| MPPS | AUC-ROC | >= 0.85 | < 0.80 |
| Credit Report Analyzer | Error Detection Precision | >= 0.90 | < 0.85 |
| Strategy Selector | Intervention Approval Rate | >= 0.75 | < 0.65 |
| Score Simulator | Mean Absolute Error (points) | <= 10 | > 15 |
| Negotiation AI | Avg Savings % | >= 30% | < 20% |
| Fraud Detection | False Positive Rate | <= 5% | > 10% |

### 10.3 Drift Detection

| Check | Frequency | Method |
|-------|-----------|--------|
| Feature distribution drift | Daily | Kolmogorov-Smirnov test |
| Prediction distribution shift | Daily | Population Stability Index (PSI) |
| Model accuracy degradation | Weekly | Backtest on recent labeled data |
| Concept drift | Monthly | Comparison of rolling window metrics |

### 10.4 Retraining Triggers

1. **Scheduled**: Monthly full retrain on all accumulated data
2. **Performance**: AUC drops below threshold for 3 consecutive days
3. **Data volume**: 50,000+ new labeled samples since last train
4. **Feature change**: New feature added or data source changed

---

## 11. Data Pipeline Architecture

```
+---------------------+
|  Raw Data Sources   |
|  (Plaid, Bureaus,   |
|   User Activity)    |
+---------+-----------+
          |
          v
+---------+-----------+
|  Feature Store      |  <-- Redis cache for real-time features
|  (Computed daily    |  <-- PostgreSQL for batch features
|   via Celery Beat)  |
+---------+-----------+
          |
          v
+---------+-----------+
|  Model Inference    |  <-- Django management commands
|  (Batch: Celery)    |  <-- Real-time: API endpoint
|  (Real-time: API)   |
+---------+-----------+
          |
          v
+---------+-----------+
|  Results Storage    |  <-- PostgreSQL (all model tables)
|  + Action Dispatch  |  <-- Celery tasks (interventions)
+---------------------+
```

---

## 12. Model Versioning & Deployment

### 12.1 Version Naming Convention

```
{model_abbreviation}-v{major}.{minor}.{patch}

Examples:
  mpps-v1.2.0    (Missed Payment Probability Score, major 1, minor 2)
  cra-v2.1.0     (Credit Report Analyzer)
  iss-v1.0.0     (Intervention Strategy Selector)
  ss-v1.3.0      (Score Simulator)
  nai-v1.0.0     (Negotiation AI)
  rpg-v1.1.0     (Recovery Plan Generator)
  fde-v1.0.0     (Fraud Detection Engine)
```

### 12.2 Model Registry

| Field | Stored In |
|-------|-----------|
| Model version | `CreditAnalysis.model_version`, `RiskScoreSnapshot` (via `score_factors`), `ScoreSimulation.model_version`, etc. |
| Training metrics | `ModelPerformanceMetric` |
| Training artifacts | AWS S3 (`/models/{version}/`) |
| Feature importance | Stored as JSON in model metadata |

### 12.3 Deployment Strategy

| Environment | Strategy | Rollback |
|-------------|----------|----------|
| Development | Direct deploy | Instant |
| Staging | Canary (10% traffic) | Instant |
| Production | Blue-Green with shadow scoring | < 5 min |

### 12.4 A/B Testing Framework

New model versions are evaluated via shadow scoring:
1. Both old and new models score every user
2. Only the production model's output drives actions
3. New model's output is logged and compared
4. Promotion after 7 days if metrics improve

---

*Model specifications subject to refinement during active development.*
