# Credit Clear - API Integration Documentation

**Version:** 1.0.0
**Last Updated:** April 2026
**Status:** In Development
**Confidential** - For Internal & Technical Review Only

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture Summary](#2-architecture-summary)
3. [Authentication & Authorization](#3-authentication--authorization)
4. [API Versioning & Standards](#4-api-versioning--standards)
5. [Endpoint Reference by Module](#5-endpoint-reference-by-module)
6. [Third-Party Integrations](#6-third-party-integrations)
7. [Webhook & Callback Architecture](#7-webhook--callback-architecture)
8. [Rate Limiting & Throttling](#8-rate-limiting--throttling)
9. [Error Handling](#9-error-handling)
10. [Data Flow Diagrams](#10-data-flow-diagrams)

---

## 1. Overview

Credit Clear exposes a RESTful API built on **Django REST Framework (DRF)** with **drf-spectacular** for OpenAPI 3.0 schema generation. All endpoints follow the `/api/v1/` prefix convention and return JSON responses.

**Base URL:**
```
Production:  https://api.creditclear.com/api/v1/
Staging:     https://staging-api.creditclear.com/api/v1/
Local:       http://localhost:8000/api/v1/
```

**Interactive Documentation:**
| Tool | URL |
|------|-----|
| Swagger UI | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| Raw OpenAPI Schema | `/api/schema/` |

---

## 2. Architecture Summary

```
                          +-------------------+
                          |   Mobile / Web    |
                          |   Applications    |
                          +--------+----------+
                                   |
                                   | HTTPS / JWT
                                   v
                          +-------------------+
                          |   Nginx / ALB     |
                          |   Load Balancer   |
                          +--------+----------+
                                   |
                    +--------------+--------------+
                    |                             |
           +-------v--------+          +---------v---------+
           |  Django API     |          |  Celery Workers   |
           |  (Gunicorn)     |          |  (Background)     |
           +-------+--------+          +---------+---------+
                    |                             |
         +----------+----------+                  |
         |          |          |                  |
    +----v---+ +---v----+ +---v-----+    +-------v-------+
    |PostgreSQL| | Redis  | |  S3     |    | Redis Broker  |
    |  (DB)   | | (Cache)| | (Media) |    | (Celery)      |
    +---------+ +--------+ +---------+    +---------------+
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 6.0.4 |
| API Layer | Django REST Framework | 3.16.1 |
| API Docs | drf-spectacular | 0.29.0 |
| Database | PostgreSQL | 18 |
| Cache / Broker | Redis | 7.x |
| Task Queue | Celery | 5.6.3 |
| Scheduler | django-celery-beat | 2.9.0 |
| Auth | django-allauth (MFA) | 65.15.1 |
| Email | SendGrid (via Anymail) | - |
| Storage | AWS S3 | - |
| WSGI Server | Gunicorn | 25.3.0 |

---

## 3. Authentication & Authorization

### 3.1 Authentication Methods

| Method | Use Case | Header Format |
|--------|----------|---------------|
| JWT Bearer Token | Mobile/SPA applications | `Authorization: Bearer <token>` |
| Session Auth | Web browser (admin) | Cookie-based |
| API Key | Server-to-server / webhooks | `X-API-Key: <key>` |

### 3.2 Auth Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register/` | Create new user account |
| `POST` | `/api/v1/auth/login/` | Obtain JWT token pair |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh expired access token |
| `POST` | `/api/v1/auth/logout/` | Blacklist refresh token |
| `POST` | `/api/v1/auth/password/reset/` | Request password reset email |
| `POST` | `/api/v1/auth/password/reset/confirm/` | Confirm password reset |
| `POST` | `/api/v1/auth/email/verify/` | Verify email address |
| `GET` | `/api/v1/auth/me/` | Get current user profile |
| `PATCH` | `/api/v1/auth/me/` | Update current user profile |

### 3.3 Role-Based Access Control (RBAC)

| Role | Access Level |
|------|-------------|
| `consumer` | Own data only; read/write personal accounts, view reports |
| `support_agent` | Read access to assigned user cases; update intervention statuses |
| `risk_analyst` | Read access to risk scores, AI engine metrics; manage thresholds |
| `admin` | Full access to all resources and system configuration |

### 3.4 Consent Management

All users must accept Terms of Service and Privacy Policy before accessing protected endpoints. Consent timestamps are tracked:
- `terms_accepted_at` - Terms of Service acceptance
- `privacy_accepted_at` - Privacy Policy acceptance
- `marketing_consent` - Optional marketing communications opt-in

---

## 4. API Versioning & Standards

### 4.1 Versioning Strategy

- **URL-based versioning:** `/api/v1/`, `/api/v2/` (future)
- Breaking changes trigger a new version; non-breaking additions are backward-compatible

### 4.2 Request/Response Standards

**Request Headers:**
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
X-Request-ID: <uuid>        # Optional, for tracing
```

**Standard Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_count": 150
  }
}
```

**Standard Error Response:**
```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Human-readable description",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

### 4.3 Pagination

All list endpoints use cursor-based or limit-offset pagination:
```
GET /api/v1/accounts/transactions/?limit=20&offset=40
```

### 4.4 Filtering & Ordering

```
GET /api/v1/risk-monitoring/alerts/?status=open&ordering=-triggered_at
GET /api/v1/accounts/linked/?account_type=bank&status=active
```

---

## 5. Endpoint Reference by Module

### 5.1 Accounts Module (`/api/v1/accounts/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/linked/` | List user's linked financial accounts |
| `POST` | `/linked/` | Initiate new account link |
| `GET` | `/linked/{id}/` | Get linked account details |
| `PATCH` | `/linked/{id}/` | Update account metadata |
| `DELETE` | `/linked/{id}/` | Disconnect a linked account |
| `POST` | `/linked/{id}/refresh/` | Force re-sync account data |
| `GET` | `/institutions/` | List supported financial institutions |
| `GET` | `/transactions/` | List transactions across all accounts |
| `GET` | `/transactions/?account={id}` | Filter transactions by account |
| `GET` | `/payment-dues/` | List upcoming payment dues |
| `GET` | `/payment-dues/overdue/` | List overdue payments |

### 5.2 Credit Graph Module (`/api/v1/credit-graph/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/nodes/` | List all credit nodes for user |
| `GET` | `/nodes/{id}/` | Get node detail with edges |
| `GET` | `/edges/` | List all relationships |
| `GET` | `/summary/` | Aggregated credit graph summary |
| `POST` | `/rebuild/` | Trigger full graph rebuild (async) |

### 5.3 AI Engine Module (`/api/v1/ai-engine/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/report-pull/` | Initiate credit report pull from bureau |
| `GET` | `/report-pull/` | List past report pulls |
| `GET` | `/report-pull/{id}/` | Get report pull details |
| `GET` | `/analyses/` | List credit analyses |
| `GET` | `/analyses/{id}/` | Get detailed analysis with errors & opportunities |
| `GET` | `/analyses/latest/` | Get most recent analysis |
| `POST` | `/recovery-plan/generate/` | Generate new 90-day recovery plan |
| `GET` | `/recovery-plans/` | List recovery plans |
| `GET` | `/recovery-plans/{id}/` | Get plan details |
| `PATCH` | `/recovery-plans/{id}/` | Update plan status |

### 5.4 Risk Monitoring Module (`/api/v1/risk-monitoring/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/scores/` | List risk score history |
| `GET` | `/scores/latest/` | Get current risk score |
| `GET` | `/scores/{id}/` | Get score snapshot with factors |
| `GET` | `/alerts/` | List risk alerts |
| `GET` | `/alerts/{id}/` | Get alert details |
| `PATCH` | `/alerts/{id}/acknowledge/` | Mark alert as acknowledged |
| `GET` | `/dashboard/` | Risk overview dashboard data |

### 5.5 Interventions Module (`/api/v1/interventions/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all interventions for user |
| `GET` | `/{id}/` | Get intervention details |
| `POST` | `/execute/` | Execute intervention strategy (auto-selected) |
| `POST` | `/{id}/retry/` | Retry a failed intervention |
| `GET` | `/{id}/communications/` | Get creditor communication logs |
| `GET` | `/creditors/` | List known creditors |
| `GET` | `/creditors/{id}/` | Get creditor details & capabilities |
| `GET` | `/creditors/{id}/strategies/` | List supported strategies per creditor |

### 5.6 Fallback Payment Module (`/api/v1/fallback-payments/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List fallback payments |
| `GET` | `/{id}/` | Get fallback payment details |
| `GET` | `/{id}/schedule/` | Get repayment schedule |
| `POST` | `/{id}/schedule/{installment}/pay/` | Make installment payment |
| `GET` | `/summary/` | Outstanding fallback balance summary |

### 5.7 Score Simulator Module (`/api/v1/score-simulator/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/simulate/` | Run score simulation |
| `POST` | `/what-if/` | Run what-if scenario |
| `GET` | `/simulations/` | List past simulations |
| `GET` | `/simulations/{id}/` | Get simulation details |

### 5.8 Credit Optimization Module (`/api/v1/credit-optimization/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/cases/` | List optimization cases |
| `GET` | `/cases/{id}/` | Get case details |
| `POST` | `/cases/` | Open new optimization case |
| `PATCH` | `/cases/{id}/` | Update case status |
| **Disputes** | | |
| `GET` | `/disputes/` | List bureau disputes |
| `POST` | `/disputes/` | File new dispute |
| `GET` | `/disputes/{id}/` | Get dispute details |
| `POST` | `/disputes/{id}/escalate/` | Escalate to CFPB |
| **Negotiations** | | |
| `GET` | `/negotiations/` | List negotiation offers |
| `POST` | `/negotiations/` | Create negotiation offer |
| `PATCH` | `/negotiations/{id}/` | Update offer (counter, accept) |
| `GET` | `/settlements/` | List active settlements |
| `GET` | `/settlements/{id}/` | Get settlement details |
| **Credit Building** | | |
| `GET` | `/building-products/` | List recommended products |
| `POST` | `/building-products/{id}/apply/` | Submit product application |
| **Fraud Monitoring** | | |
| `GET` | `/fraud-alerts/` | List fraud alerts |
| `GET` | `/fraud-alerts/{id}/` | Get alert details |
| `POST` | `/fraud-alerts/{id}/dispute/` | File fraud dispute |
| **Bill Negotiation** | | |
| `GET` | `/bill-negotiations/` | List bill negotiations |
| `POST` | `/bill-negotiations/` | Start new bill negotiation |
| `GET` | `/bill-negotiations/{id}/` | Get negotiation result |

### 5.9 Recovery Roadmap Module (`/api/v1/recovery-roadmap/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/milestones/` | List roadmap milestones |
| `GET` | `/milestones/{id}/` | Get milestone with actions |
| `PATCH` | `/milestones/{id}/` | Update milestone status |
| `GET` | `/milestones/{id}/actions/` | List actions for milestone |
| `PATCH` | `/actions/{id}/` | Update action status |
| `GET` | `/progress/` | Overall roadmap progress summary |

### 5.10 Gamification Module (`/api/v1/gamification/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/balance/` | Get user's points balance & level |
| `GET` | `/rewards/` | List earned rewards history |
| `GET` | `/badges/` | List all available badges |
| `GET` | `/badges/earned/` | List user's earned badges |
| `GET` | `/leaderboard/` | Anonymized leaderboard |

### 5.11 Education Module (`/api/v1/education/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/content/` | List published educational content |
| `GET` | `/content/{slug}/` | Get content detail |
| `GET` | `/progress/` | List user's learning progress |
| `POST` | `/progress/{content_id}/` | Update progress / mark complete |
| `GET` | `/recommended/` | AI-recommended content for user |

### 5.12 Notifications Module (`/api/v1/notifications/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List user notifications |
| `GET` | `/{id}/` | Get notification detail |
| `PATCH` | `/{id}/read/` | Mark notification as read |
| `POST` | `/read-all/` | Mark all as read |
| `GET` | `/preferences/` | Get notification preferences |
| `PUT` | `/preferences/` | Update notification preferences |
| `GET` | `/unread-count/` | Get unread notification count |

### 5.13 Analytics Module (`/api/v1/analytics/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/dashboard/` | User analytics dashboard |
| `GET` | `/score-history/` | Credit score trend over time |
| `GET` | `/savings-summary/` | Total savings from interventions & negotiations |
| `GET` | `/activity-log/` | User activity event log |

---

## 6. Third-Party Integrations

### 6.1 Integration Map

| Integration | Purpose | Protocol | Status |
|-------------|---------|----------|--------|
| **Plaid** | Bank account linking, transaction sync | REST API + Webhooks | Planned |
| **Experian API** | Credit report pull, score | REST API (mTLS) | Planned |
| **Equifax API** | Credit report pull, score | REST API (mTLS) | Planned |
| **TransUnion API** | Credit report pull, score | REST API (mTLS) | Planned |
| **Creditor APIs** | Payment modifications, extensions | REST / SOAP (varies) | Planned |
| **SendGrid** | Transactional email delivery | REST API | Configured |
| **AWS S3** | Media & static file storage | AWS SDK | Configured |
| **Stripe / Payment Provider** | Fallback payment processing | REST API + Webhooks | Planned |
| **CFPB eCFR** | Complaint filing & escalation | REST API | Planned |
| **Dark Web Monitoring** | Identity data breach scanning | REST API | Planned |
| **BNPL Providers** | Buy Now Pay Later facilitation | REST API | Planned |

### 6.2 Integration Data Flow

```
User Request --> Credit Clear API --> Celery Task (async)
                                          |
                                          +--> Plaid API (account data)
                                          +--> Bureau APIs (credit reports)
                                          +--> Creditor APIs (interventions)
                                          +--> Payment Provider (fallback pay)
                                          |
                                     Response stored in DB
                                          |
                                     Notification sent to user
```

### 6.3 Webhook Inbound Endpoints

| Provider | Endpoint | Purpose |
|----------|----------|---------|
| Plaid | `/api/v1/webhooks/plaid/` | Account updates, transaction sync |
| Stripe | `/api/v1/webhooks/stripe/` | Payment status changes |
| Bureau | `/api/v1/webhooks/bureau/` | Dispute status updates |

---

## 7. Webhook & Callback Architecture

### 7.1 Inbound Webhooks (from third parties)
- Signature verification on all incoming webhooks
- Idempotency via unique event IDs
- Events queued to Celery for async processing
- Failed webhook processing retried with exponential backoff

### 7.2 Outbound Webhooks (optional)
- Configurable webhook URLs per application
- Events: `risk.alert.triggered`, `intervention.completed`, `score.changed`, `fraud.detected`
- HMAC-SHA256 signed payloads
- Retry policy: 3 attempts with exponential backoff

---

## 8. Rate Limiting & Throttling

| Scope | Limit | Window |
|-------|-------|--------|
| Anonymous | 20 requests | per minute |
| Authenticated (consumer) | 120 requests | per minute |
| Authenticated (admin) | 600 requests | per minute |
| Bureau Pull | 3 requests | per day per user |
| Score Simulation | 20 requests | per hour per user |
| Webhook Inbound | 1000 requests | per minute |

---

## 9. Error Handling

### 9.1 HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | No Content (successful delete) |
| `400` | Bad Request / Validation Error |
| `401` | Unauthorized (missing/invalid token) |
| `403` | Forbidden (insufficient role/permissions) |
| `404` | Not Found |
| `409` | Conflict (duplicate resource) |
| `422` | Unprocessable Entity |
| `429` | Too Many Requests |
| `500` | Internal Server Error |
| `503` | Service Unavailable |

### 9.2 Application Error Codes

| Code | Description |
|------|-------------|
| `AUTH_001` | Invalid credentials |
| `AUTH_002` | Token expired |
| `AUTH_003` | Email not verified |
| `AUTH_004` | Consent not provided |
| `ACCT_001` | Account link failed |
| `ACCT_002` | Account sync in progress |
| `RISK_001` | Risk score computation failed |
| `INTV_001` | Creditor API unreachable |
| `INTV_002` | Intervention strategy not supported |
| `INTV_003` | Intervention already in progress |
| `PAY_001` | Payment processing failed |
| `PAY_002` | Insufficient funds |
| `OPT_001` | Dispute submission failed |
| `OPT_002` | Bureau not responding |

---

## 10. Data Flow Diagrams

### 10.1 Onboarding Flow

```
App                       API                      Celery              External
  |                        |                         |                    |
  |-- POST /auth/register -->                        |                    |
  |<-- 201 User Created --|                          |                    |
  |                        |-- send_verification --> |                    |
  |                        |                         |-- SendGrid Email ->|
  |-- POST /auth/verify -->|                         |                    |
  |<-- 200 Verified -------|                         |                    |
  |-- POST /accounts/linked/ ->                      |                    |
  |<-- 202 Accepted -------|-- link_account -------> |                    |
  |                        |                         |--- Plaid API ----->|
  |                        |                         |<-- Account Data ---|
  |                        |                         |-- build_credit_graph -->
  |                        |                         |-- run_ai_analysis ----->
  |<-- Notification -------|<-- push_notification ---|                    |
```

### 10.2 Risk Alert & Intervention Flow

```
Celery Beat               Celery Worker             API                External
  |                          |                        |                   |
  |-- trigger_risk_scan ---> |                        |                   |
  |                          |-- compute scores       |                   |
  |                          |-- threshold check      |                   |
  |                          |   (probability >= 70%) |                   |
  |                          |-- create RiskAlert     |                   |
  |                          |-- select_strategy      |                   |
  |                          |-- execute_intervention  |                   |
  |                          |                        |                   |
  |                          |------------- Creditor API Request -------->|
  |                          |<------------ Creditor API Response --------|
  |                          |                        |                   |
  |                          |-- [APPROVED] notify_user                   |
  |                          |-- [DENIED] initiate_fallback_payment       |
  |                          |------------- Payment Provider ------------>|
  |                          |<------------ Payment Confirmation ---------|
  |                          |-- create_repayment_schedule                |
  |                          |-- push_notification --> |                   |
```

---

*All endpoints are subject to change during active development.*
