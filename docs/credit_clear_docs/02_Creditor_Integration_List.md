# Credit Clear - Creditor Integration List

**Version:** 1.0.0
**Last Updated:** April 2026
**Status:** In Development
**Confidential** - For Internal & Technical Review Only

---

## Table of Contents

1. [Overview](#1-overview)
2. [Integration Architecture](#2-integration-architecture)
3. [Credit Bureau Integrations](#3-credit-bureau-integrations)
4. [Financial Data Aggregators](#4-financial-data-aggregators)
5. [Creditor / Lender Integrations](#5-creditor--lender-integrations)
6. [Payment Providers](#6-payment-providers)
7. [BNPL Providers](#7-bnpl-providers)
8. [Fraud & Identity Monitoring](#8-fraud--identity-monitoring)
9. [Communication & Notification Providers](#9-communication--notification-providers)
10. [Regulatory & Compliance](#10-regulatory--compliance)
11. [Integration Status Summary](#11-integration-status-summary)
12. [Integration Roadmap](#12-integration-roadmap)

---

## 1. Overview

Credit Clear integrates with external financial systems to deliver its core value proposition: proactive credit protection, automated interventions, and credit optimization. This document catalogs every integration, its purpose, current status, and technical details.

### Integration Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Credit Bureaus | 3 | Credit report pulls, dispute filing |
| Data Aggregators | 2 | Bank/card/loan account linking |
| Creditors / Lenders | 10+ | Payment modifications, negotiations |
| Payment Providers | 2 | Fallback payments, repayments |
| BNPL Providers | 3 | Buy Now Pay Later facilitation |
| Fraud Monitoring | 2 | Dark web scanning, identity protection |
| Communication | 3 | Email, SMS, push notifications |
| Regulatory | 1 | CFPB complaint filing |

---

## 2. Integration Architecture

### 2.1 Data Model

Each creditor/integration is tracked via the `Creditor` model:

```
Creditor
  - name                        # Display name
  - slug                        # Unique identifier
  - api_endpoint                # Base API URL
  - api_key_ref                 # Reference to secrets manager key
  - supported_strategies[]      # JSON: ["extension", "grace_period", ...]
  - contact_phone               # Fallback phone contact
  - contact_email               # Fallback email contact
  - supports_auto_negotiation   # Boolean: can we negotiate programmatically?
  - avg_response_time_hours     # Historical average response time
  - success_rate                # Historical success rate (%)
  - is_active                   # Currently accepting requests?
```

### 2.2 Communication Pattern

```
+-------------------+       +-------------------+       +------------------+
|                   |       |                   |       |                  |
|  Credit Clear     | ----> |  Celery Worker    | ----> |  External API    |
|  API Server       |       |  (Async Task)     |       |  (Creditor/      |
|                   |       |                   |       |   Bureau/etc.)   |
+-------------------+       +--------+----------+       +--------+---------+
                                     |                           |
                                     v                           |
                            +--------+----------+                |
                            |  Communication    |<---------------+
                            |  Log (DB)         |  Response stored
                            +-------------------+
```

All external API calls are:
- **Asynchronous** (executed via Celery tasks)
- **Fully logged** in `CreditorCommunicationLog` (request/response/latency)
- **Retry-enabled** with exponential backoff
- **Circuit-breaker protected** to prevent cascade failures

---

## 3. Credit Bureau Integrations

### 3.1 Experian

| Field | Detail |
|-------|--------|
| **Purpose** | Credit report pull, credit score, dispute filing |
| **API Type** | REST API with mTLS |
| **Authentication** | OAuth 2.0 Client Credentials + mTLS Certificate |
| **Endpoints Used** | Credit Profile, Consumer Dispute, Fraud Alert |
| **Data Retrieved** | Credit score, trade lines, inquiries, public records, collections |
| **Frequency** | On-demand (max 3 pulls/day per user) |
| **Sandbox Available** | Yes |
| **Status** | **Planned** |
| **Priority** | P0 - Critical |

**Data Mapping:**
| Experian Field | Credit Clear Model | Field |
|---------------|--------------------|-------|
| Credit Score | `CreditReportPull` | `score_at_pull` |
| Trade Lines | `CreditReportPull` | `total_accounts` |
| Total Debt | `CreditReportPull` | `total_debt` |
| Collections | `CreditReportPull` | `open_collections` |
| Derogatory Marks | `CreditReportPull` | `derogatory_marks` |
| Inquiries | `CreditReportPull` | `hard_inquiries` |
| Utilization | `CreditReportPull` | `credit_utilization` |
| Raw JSON | `CreditReportPull` | `raw_report` |

---

### 3.2 Equifax

| Field | Detail |
|-------|--------|
| **Purpose** | Credit report pull, score, dispute filing |
| **API Type** | REST API with mTLS |
| **Authentication** | API Key + mTLS Certificate |
| **Status** | **Planned** |
| **Priority** | P0 - Critical |

---

### 3.3 TransUnion

| Field | Detail |
|-------|--------|
| **Purpose** | Credit report pull, score, dispute filing |
| **API Type** | REST API with mTLS |
| **Authentication** | OAuth 2.0 + mTLS |
| **Status** | **Planned** |
| **Priority** | P0 - Critical |

---

## 4. Financial Data Aggregators

### 4.1 Plaid

| Field | Detail |
|-------|--------|
| **Purpose** | Bank account linking, transaction sync, balance checks, income verification |
| **API Type** | REST API + Webhooks |
| **Authentication** | Client ID + Secret |
| **Products Used** | Auth, Transactions, Balance, Identity, Liabilities |
| **Webhook Events** | `TRANSACTIONS_SYNC`, `ITEM_ERROR`, `BALANCE_UPDATE` |
| **Status** | **Planned** |
| **Priority** | P0 - Critical |

**Data Mapping:**
| Plaid Entity | Credit Clear Model | Field |
|-------------|-------------------|-------|
| Account | `LinkedAccount` | `external_account_id`, `balance`, etc. |
| Transaction | `Transaction` | All transaction fields |
| Institution | `FinancialInstitution` | `name`, `provider_key` |

### 4.2 MX (Alternate / Backup)

| Field | Detail |
|-------|--------|
| **Purpose** | Backup aggregator for institutions not covered by Plaid |
| **API Type** | REST API |
| **Status** | **Planned** |
| **Priority** | P2 - Nice to Have |

---

## 5. Creditor / Lender Integrations

### 5.1 Integration Status Matrix

| # | Creditor Category | Example Creditors | Auto-Negotiate | Supported Strategies | Status |
|---|-------------------|-------------------|----------------|---------------------|--------|
| 1 | **Major Banks** | Chase, Bank of America, Wells Fargo, Citi | Planned | Extension, Grace Period, Due Date Change | **Planned** |
| 2 | **Credit Card Issuers** | Capital One, Discover, Amex | Planned | Extension, Installment, Interest Reduction | **Planned** |
| 3 | **Auto Lenders** | Ally Financial, Capital One Auto | Planned | Extension, Due Date Change | **Planned** |
| 4 | **Student Loans** | Nelnet, MOHELA, FedLoan | Planned | Extension, Forbearance, IDR Plan | **Planned** |
| 5 | **Mortgage Servicers** | Mr. Cooper, Nationstar | Planned | Extension, Forbearance | **Planned** |
| 6 | **Medical Billing** | Major hospital networks, billing agencies | Planned | Payment Plan, Settlement | **Planned** |
| 7 | **Collections** | Midland Credit, Portfolio Recovery | Planned | Settlement, Pay-for-Delete | **Planned** |
| 8 | **Utilities** | Major utility providers | Planned | Extension, Payment Plan | **Planned** |
| 9 | **Telecom** | AT&T, Verizon, T-Mobile | Planned | Extension, Plan Change | **Planned** |
| 10 | **Insurance** | Major insurance carriers | Planned | Payment Plan, Rate Reduction | **Planned** |

### 5.2 Creditor Communication Channels

| Channel | Use Case | Priority |
|---------|----------|----------|
| **Direct API** | Automated payment modification requests | Primary |
| **Secure Portal (RPA)** | Creditors without APIs - robotic process automation | Secondary |
| **Secure Email** | Formal dispute letters, settlement offers | Tertiary |
| **Phone (AI Voice)** | Creditors requiring phone contact | Future |

### 5.3 Supported Intervention Strategies Per Creditor Type

| Strategy | Banks | Cards | Auto | Student | Medical | Collections |
|----------|-------|-------|------|---------|---------|-------------|
| Payment Extension | Yes | Yes | Yes | Yes | Yes | No |
| Grace Period | Yes | Yes | No | Yes | No | No |
| Due Date Change | Yes | Yes | Yes | No | No | No |
| Installment Conversion | No | Yes | No | No | Yes | No |
| BNPL Financing | No | Yes | No | No | Yes | No |
| Settlement | No | No | No | No | Yes | Yes |
| Pay-for-Delete | No | No | No | No | No | Yes |
| Interest Reduction | No | Yes | Yes | Yes | No | No |

---

## 6. Payment Providers

### 6.1 Stripe

| Field | Detail |
|-------|--------|
| **Purpose** | Fallback payment processing, repayment collection |
| **API Type** | REST API + Webhooks |
| **Features Used** | Payment Intents, Subscriptions (repayment), Webhooks |
| **Webhook Events** | `payment_intent.succeeded`, `payment_intent.failed`, `invoice.paid` |
| **Status** | **Planned** |
| **Priority** | P0 - Critical |

### 6.2 Dwolla (ACH Transfers)

| Field | Detail |
|-------|--------|
| **Purpose** | Direct bank-to-bank transfers for settlements/repayments |
| **API Type** | REST API |
| **Status** | **Planned** |
| **Priority** | P1 - Important |

---

## 7. BNPL Providers

### 7.1 Integration Plan

| Provider | Purpose | API Type | Status |
|----------|---------|----------|--------|
| **Affirm** | BNPL for denied intervention fallback | REST API | **Planned** |
| **Klarna** | BNPL alternative provider | REST API | **Planned** |
| **Afterpay** | BNPL for smaller amounts | REST API | **Planned** |

**BNPL Data Mapping:**
| BNPL Field | Credit Clear Model | Field |
|-----------|-------------------|-------|
| Loan ID | `FallbackPayment` | `bnpl_reference` |
| Provider | `FallbackPayment` | `bnpl_provider` |
| Interest Rate | `FallbackPayment` | `interest_rate` |
| Installments | `FallbackPayment` | `total_installments` |
| Total Amount | `FallbackPayment` | `total_repayable` |

---

## 8. Fraud & Identity Monitoring

### 8.1 Have I Been Pwned / SpyCloud

| Field | Detail |
|-------|--------|
| **Purpose** | Dark web monitoring, data breach detection |
| **Data Checked** | Email, SSN, phone, addresses |
| **Frequency** | Daily automated scan |
| **Alert Types** | `dark_web`, `identity_theft` |
| **Status** | **Planned** |
| **Priority** | P1 - Important |

### 8.2 Bureau Fraud Alert Services

| Field | Detail |
|-------|--------|
| **Purpose** | New account alerts, hard inquiry monitoring |
| **Source** | Experian, Equifax, TransUnion fraud alert APIs |
| **Alert Types** | `new_account`, `hard_inquiry`, `address_change` |
| **Status** | **Planned** |
| **Priority** | P1 - Important |

**Fraud Alert Data Mapping:**
| External Data | Credit Clear Model | Field |
|--------------|-------------------|-------|
| Alert Type | `FraudAlert` | `alert_type` |
| Severity | `FraudAlert` | `severity` |
| Exposed Data | `FraudAlert` | `exposed_data_types` |
| Source | `FraudAlert` | `source` |
| Affected Account | `FraudAlert` | `affected_account` |

---

## 9. Communication & Notification Providers

### 9.1 SendGrid (Email)

| Field | Detail |
|-------|--------|
| **Purpose** | Transactional emails (verification, alerts, reports) |
| **API Type** | REST API via django-anymail |
| **Status** | **Configured** |
| **Priority** | P0 - Critical |

### 9.2 Twilio (SMS)

| Field | Detail |
|-------|--------|
| **Purpose** | SMS notifications for critical alerts |
| **API Type** | REST API |
| **Status** | **Planned** |
| **Priority** | P1 - Important |

### 9.3 Firebase Cloud Messaging (Push)

| Field | Detail |
|-------|--------|
| **Purpose** | Mobile push notifications |
| **API Type** | REST API |
| **Status** | **Planned** |
| **Priority** | P1 - Important |

---

## 10. Regulatory & Compliance

### 10.1 CFPB Complaint Portal

| Field | Detail |
|-------|--------|
| **Purpose** | Escalate unresolved disputes to Consumer Financial Protection Bureau |
| **Data Filed** | Dispute reason, bureau, account details, evidence |
| **Tracked In** | `BureauDispute.cfpb_complaint_id` |
| **Status** | **Planned** |
| **Priority** | P1 - Important |

---

## 11. Integration Status Summary

### Overall Status Dashboard

| Status | Count | Integrations |
|--------|-------|-------------|
| **Live** | 0 | - |
| **Configured** | 1 | SendGrid |
| **In Development** | 0 | - |
| **Planned** | 18 | All others |

### Status by Priority

| Priority | Integration | Target Phase |
|----------|-------------|-------------|
| **P0 - Critical** | Plaid, Experian, Equifax, TransUnion, Stripe, SendGrid | Phase 1 |
| **P1 - Important** | Twilio, FCM, SpyCloud, Dwolla, CFPB, Bureau Fraud APIs | Phase 2 |
| **P2 - Nice to Have** | MX, Affirm, Klarna, Afterpay, AI Voice | Phase 3 |

---

## 12. Integration Roadmap

### Phase 1: Core Infrastructure (Months 1-3)

```
Month 1                    Month 2                    Month 3
+---------------------+    +---------------------+    +---------------------+
| - Plaid (account    |    | - Experian API      |    | - Equifax API       |
|   linking)          |    | - Stripe (fallback  |    | - TransUnion API    |
| - SendGrid (done)   |    |   payments)         |    | - Bureau dispute    |
| - FCM setup        |    | - Twilio (SMS)      |    |   filing via APIs   |
+---------------------+    +---------------------+    +---------------------+
```

### Phase 2: Creditor Network (Months 4-6)

```
Month 4                    Month 5                    Month 6
+---------------------+    +---------------------+    +---------------------+
| - Major bank APIs   |    | - Collections APIs  |    | - Medical billing   |
|   (Chase, BofA)     |    | - SpyCloud/dark web |    | - CFPB integration  |
| - Credit card APIs  |    | - Dwolla (ACH)      |    | - Auto lender APIs  |
|   (CapOne, Discover)|    |                     |    |                     |
+---------------------+    +---------------------+    +---------------------+
```

### Phase 3: Extended Network (Months 7-9)

```
Month 7                    Month 8                    Month 9
+---------------------+    +---------------------+    +---------------------+
| - BNPL providers    |    | - Student loan       |    | - AI voice agent    |
|   (Affirm, Klarna)  |    |   servicers          |    | - MX (backup agg.)  |
| - Utility providers |    | - Mortgage servicers |    | - Full creditor     |
| - Telecom providers |    | - Insurance carriers |    |   network live      |
+---------------------+    +---------------------+    +---------------------+
```

---

*Integration details subject to change during active development.*
