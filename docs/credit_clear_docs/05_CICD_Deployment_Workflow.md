# Credit Clear - CI/CD & Deployment Workflow Document

**Version:** 1.0.0
**Last Updated:** April 2026
**Status:** In Development
**Confidential** - For Internal & Technical Review Only

---

## Table of Contents

1. [Overview](#1-overview)
2. [Environment Architecture](#2-environment-architecture)
3. [CI Pipeline (Continuous Integration)](#3-ci-pipeline-continuous-integration)
4. [CD Pipeline (Continuous Deployment)](#4-cd-pipeline-continuous-deployment)
5. [Infrastructure Architecture](#5-infrastructure-architecture)
6. [Database Migration Strategy](#6-database-migration-strategy)
7. [Secret Management](#7-secret-management)
8. [Monitoring & Observability](#8-monitoring--observability)
9. [Incident Response & Rollback](#9-incident-response--rollback)
10. [Security & Compliance](#10-security--compliance)
11. [Development Workflow](#11-development-workflow)
12. [Disaster Recovery](#12-disaster-recovery)

---

## 1. Overview

Credit Clear uses a modern CI/CD pipeline powered by **GitHub Actions** for automated testing, building, and deployment. The system follows a trunk-based development model with feature branches, automated quality gates, and progressive deployment to production.

### Pipeline Summary

```
Developer Push --> GitHub Actions CI --> Quality Gates --> Build & Package
                                                              |
                                                              v
                    Production <-- Staging <-- Docker Image Registry
```

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Automated Everything** | No manual steps between commit and deploy |
| **Quality Gates** | Code cannot reach production without passing all checks |
| **Immutable Artifacts** | Docker images are built once, promoted across environments |
| **Progressive Delivery** | Staging -> Canary (10%) -> Production (100%) |
| **Zero-Downtime** | Rolling deployments with health checks |
| **Instant Rollback** | Previous version always available, < 2 min rollback |

---

## 2. Environment Architecture

### 2.1 Environments

| Environment | Purpose | URL | Deployment Trigger |
|-------------|---------|-----|-------------------|
| **Local** | Developer machines | `localhost:8000` | Manual |
| **CI** | Automated testing | Ephemeral (GitHub Actions) | Every push/PR |
| **Staging** | Pre-production validation | `staging.creditclear.com` | Merge to `main` |
| **Production** | Live user traffic | `creditclear.com` | Manual promotion from staging |

### 2.2 Environment Configuration

| Setting | Local | CI | Staging | Production |
|---------|-------|-----|---------|------------|
| `DEBUG` | True | False | False | False |
| Database | Local PostgreSQL | GitHub Service (PG 18) | AWS RDS (PG 18) | AWS RDS (PG 18, Multi-AZ) |
| Redis | Local Redis | GitHub Service (Redis 7.2) | AWS ElastiCache | AWS ElastiCache (Cluster) |
| Storage | Local filesystem | - | AWS S3 | AWS S3 |
| Email | Console backend | - | SendGrid (sandbox) | SendGrid (production) |
| SSL | None | - | ACM Certificate | ACM Certificate |
| Domain | localhost | - | staging.creditclear.com | creditclear.com |

---

## 3. CI Pipeline (Continuous Integration)

### 3.1 Pipeline Architecture

```
+-------------------+
|  Developer Push   |
|  or PR Created    |
+---------+---------+
          |
          v
+---------+---------+     +---------+---------+
|    Linter Job     |     |    Pytest Job     |
|  (runs in parallel)|     |  (runs in parallel)|
|                   |     |                   |
|  1. Checkout code |     |  1. Checkout code |
|  2. Setup Python  |     |  2. Install uv    |
|  3. Run pre-commit|     |  3. Setup Python  |
|     - trailing-ws |     |  4. Install deps  |
|     - eof-fixer   |     |  5. Check migrations|
|     - ruff-check  |     |  6. Run migrations|
|     - ruff-format |     |  7. Run pytest    |
|     - djlint      |     |                   |
|     - django-upgrade     |                   |
+-------------------+     +-------------------+
          |                         |
          +------------+------------+
                       |
                       v
              +--------+---------+
              |  All Checks Pass |
              |  -> PR Mergeable |
              +------------------+
```

### 3.2 Current CI Workflow (`.github/workflows/ci.yml`)

**Trigger:** Push to `main` or Pull Request to `main`

**Job 1: Linter**
| Step | Tool | Purpose |
|------|------|---------|
| 1 | `pre-commit` | Run all pre-commit hooks |
| - | `trailing-whitespace` | Remove trailing whitespace |
| - | `end-of-file-fixer` | Ensure files end with newline |
| - | `check-json/toml/xml/yaml` | Validate config file syntax |
| - | `debug-statements` | No leftover `print()` / `pdb` |
| - | `detect-private-key` | Prevent key leaks |
| - | `django-upgrade` | Auto-upgrade Django code to 6.0 patterns |
| - | `ruff-check` | Python linting (200+ rules) |
| - | `ruff-format` | Python code formatting |
| - | `djlint` | Django template linting & formatting |
| - | `pyproject-fmt` | Keep pyproject.toml formatted |

**Job 2: Pytest**
| Step | Tool | Purpose |
|------|------|---------|
| 1 | PostgreSQL 18 service | Test database |
| 2 | Redis 7.2 service | Test cache/broker |
| 3 | `uv sync --locked` | Install exact locked dependencies |
| 4 | `makemigrations --check` | Ensure no missing migrations |
| 5 | `migrate` | Apply all migrations |
| 6 | `pytest` | Run full test suite |

### 3.3 Quality Gates (Required to Merge)

| Gate | Tool | Threshold | Blocking |
|------|------|-----------|----------|
| Linting | Ruff | Zero errors | Yes |
| Formatting | Ruff Format | Zero diff | Yes |
| Template Lint | djLint | Zero errors | Yes |
| Unit Tests | Pytest | 100% pass | Yes |
| Migration Check | Django | No pending migrations | Yes |
| Secret Detection | pre-commit | Zero findings | Yes |
| Type Checking | mypy | Zero errors (planned) | Planned |
| Test Coverage | Coverage.py | >= 80% (planned) | Planned |
| Security Scan | Dependabot | No critical CVEs | Yes |

### 3.4 Dependency Management

| Tool | Purpose |
|------|---------|
| **uv** | Fast Python package manager (lockfile: `uv.lock`) |
| **Dependabot** | Automated dependency update PRs (`.github/dependabot.yml`) |
| **pre-commit.ci** | Auto-update pre-commit hooks weekly |

---

## 4. CD Pipeline (Continuous Deployment)

### 4.1 Deployment Pipeline (Planned)

```
+------------------+    +------------------+    +-------------------+
|  Merge to main   |    |  Build & Push    |    |  Deploy Staging   |
|  (CI passes)     |--->|  Docker Image    |--->|  (auto)           |
+------------------+    +------------------+    +--------+----------+
                                                         |
                                                         v
                                                +--------+----------+
                                                |  Staging Tests    |
                                                |  (smoke + E2E)   |
                                                +--------+----------+
                                                         |
                                                         v
                                                +--------+----------+
                                                |  Manual Approval  |
                                                |  (deploy to prod) |
                                                +--------+----------+
                                                         |
                                                         v
                                                +--------+----------+
                                                |  Deploy Prod      |
                                                |  (rolling update) |
                                                +--------+----------+
                                                         |
                                                         v
                                                +--------+----------+
                                                |  Post-Deploy      |
                                                |  Health Check     |
                                                +-------------------+
```

### 4.2 Docker Build (Planned)

**Multi-stage Dockerfile:**

```
Stage 1: Builder
  - Install Python dependencies via uv
  - Collect static files
  - Compile translations

Stage 2: Runtime
  - Copy dependencies from builder
  - Copy application code
  - Set non-root user
  - Configure Gunicorn entrypoint
```

**Image Tagging Strategy:**

| Tag | Purpose | Example |
|-----|---------|---------|
| `git-sha` | Immutable reference | `credit-clear:a1b2c3d` |
| `latest` | Most recent build | `credit-clear:latest` |
| `staging` | Currently on staging | `credit-clear:staging` |
| `production` | Currently in production | `credit-clear:production` |

### 4.3 Deployment Strategy

| Component | Strategy | Details |
|-----------|----------|---------|
| **Django API** | Rolling update | 2+ replicas, one at a time, health check gates |
| **Celery Workers** | Rolling update | Graceful shutdown (SIGTERM, wait for tasks) |
| **Celery Beat** | Single instance | Lock-based (only one Beat runs at a time) |
| **Migrations** | Pre-deploy job | Run before new code deploys |
| **Static Files** | S3 + CloudFront | `collectstatic` during Docker build |

### 4.4 Zero-Downtime Deployment Steps

```
1. Build new Docker image
2. Push to container registry (ECR)
3. Run database migrations (pre-deploy job)
4. Deploy new image to staging
5. Run staging smoke tests
6. [Manual approval]
7. Deploy new image to production (rolling)
   a. Start new container with new image
   b. Wait for health check to pass
   c. Route traffic to new container
   d. Drain old container (finish active requests)
   e. Stop old container
   f. Repeat for all replicas
8. Run post-deploy health checks
9. Notify team of successful deployment
```

---

## 5. Infrastructure Architecture

### 5.1 AWS Infrastructure (Planned)

```
                        +-------------------+
                        |   Route 53 (DNS)  |
                        +--------+----------+
                                 |
                        +--------v----------+
                        |   CloudFront      |
                        |   (Static/CDN)    |
                        +--------+----------+
                                 |
                        +--------v----------+
                        |   ALB             |
                        |   (Load Balancer) |
                        +--------+----------+
                                 |
                    +------------+------------+
                    |                         |
           +--------v-------+       +--------v--------+
           |   ECS Fargate  |       |   ECS Fargate   |
           |   (Django API) |       |   (Celery       |
           |   2+ tasks     |       |    Workers)     |
           +-------+--------+       +--------+--------+
                    |                         |
         +----------+----------+              |
         |          |          |              |
   +-----v----+ +--v------+ +-v--------+  +--v---------+
   |  RDS      | | Elasti- | |  S3      |  | ElastiCache|
   |  (PG 18)  | | Cache   | | (Media)  |  | (Redis     |
   |  Multi-AZ | | (Redis) | |          |  |  Broker)   |
   +-----------+ +---------+ +----------+  +------------+
```

### 5.2 Component Specifications

| Component | Service | Spec | Purpose |
|-----------|---------|------|---------|
| Compute (API) | ECS Fargate | 2 vCPU, 4GB RAM, 2+ tasks | Django + Gunicorn |
| Compute (Workers) | ECS Fargate | 2 vCPU, 4GB RAM, 2+ tasks | Celery workers |
| Compute (Beat) | ECS Fargate | 0.5 vCPU, 1GB RAM, 1 task | Celery Beat scheduler |
| Database | RDS PostgreSQL 18 | db.r6g.large, Multi-AZ | Primary datastore |
| Cache | ElastiCache Redis 7 | cache.r6g.large | Session cache |
| Broker | ElastiCache Redis 7 | cache.r6g.large | Celery message broker |
| Storage | S3 | Standard | Media files, static assets |
| CDN | CloudFront | Global edge | Static file delivery |
| DNS | Route 53 | - | Domain management |
| Load Balancer | ALB | - | HTTPS termination, routing |
| Container Registry | ECR | - | Docker image storage |
| Secrets | Secrets Manager | - | API keys, credentials |
| Logging | CloudWatch | - | Centralized logging |
| Monitoring | CloudWatch + Sentry | - | Metrics and error tracking |

---

## 6. Database Migration Strategy

### 6.1 Migration Workflow

```
1. Developer creates migration locally:
   python manage.py makemigrations

2. Migration committed with code in same PR

3. CI verifies: makemigrations --check (no pending)

4. During deployment (pre-deploy step):
   python manage.py migrate --noinput

5. New code deployed AFTER migrations complete
```

### 6.2 Migration Safety Rules

| Rule | Description |
|------|-------------|
| **No destructive migrations in one step** | Dropping columns/tables requires 2-step deploy: (1) stop using column, (2) drop column |
| **Always add nullable columns** | New columns must be `null=True` or have a `default` to avoid locking large tables |
| **Test migrations both ways** | Verify `migrate` and `migrate --reverse` work |
| **No data migrations with schema changes** | Separate schema migrations from data migrations |
| **Index creation: CONCURRENTLY** | Large table indexes use `CREATE INDEX CONCURRENTLY` via `SeparateDatabaseAndState` |

### 6.3 Backup Before Migration

```
Pre-deploy:
  1. Create RDS snapshot (automatic, labeled with deploy version)
  2. Run migration
  3. If migration fails: restore from snapshot, abort deploy
```

---

## 7. Secret Management

### 7.1 Secret Storage

| Secret Type | Storage | Access Method |
|-------------|---------|--------------|
| Django SECRET_KEY | AWS Secrets Manager | Environment variable |
| Database URL | AWS Secrets Manager | Environment variable |
| Redis URL | AWS Secrets Manager | Environment variable |
| SendGrid API Key | AWS Secrets Manager | Environment variable |
| Plaid Client ID/Secret | AWS Secrets Manager | Environment variable |
| Bureau API Certificates | AWS Secrets Manager | Mounted as file |
| Stripe API Keys | AWS Secrets Manager | Environment variable |
| AWS Access Keys | IAM Roles (not keys) | ECS Task Role |

### 7.2 Secret Rotation

| Secret | Rotation Frequency | Method |
|--------|-------------------|--------|
| Django SECRET_KEY | Quarterly | Manual rotation, session invalidation |
| Database Password | Monthly | AWS Secrets Manager auto-rotation |
| API Keys (3rd party) | Annually | Manual rotation |
| mTLS Certificates | Before expiry | Auto-renewal via ACM |

### 7.3 Local Development

```
- Secrets in .env file (git-ignored)
- .env.example committed with placeholder values
- django-environ reads .env when DJANGO_READ_DOT_ENV_FILE=True
```

---

## 8. Monitoring & Observability

### 8.1 Monitoring Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| **Application Errors** | Sentry | Exception tracking, error grouping |
| **Application Metrics** | CloudWatch Custom Metrics | Business metrics, API latency |
| **Infrastructure** | CloudWatch | CPU, memory, disk, network |
| **Logs** | CloudWatch Logs | Centralized log aggregation |
| **Uptime** | CloudWatch Synthetics / UptimeRobot | Endpoint availability |
| **Database** | RDS Performance Insights | Query performance, connections |
| **Celery** | Flower + CloudWatch | Task success/failure, queue depth |

### 8.2 Key Metrics & Alerts

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| API Response Time (p95) | > 500ms | > 2000ms | Scale up, investigate |
| API Error Rate (5xx) | > 1% | > 5% | Page on-call |
| Celery Queue Depth | > 100 | > 500 | Scale workers |
| Celery Task Failure Rate | > 5% | > 15% | Investigate, pause tasks |
| Database Connections | > 80% pool | > 95% pool | Scale RDS |
| Database CPU | > 70% | > 90% | Scale RDS |
| Redis Memory | > 70% | > 90% | Scale ElastiCache |
| Disk Usage | > 70% | > 90% | Clean up / expand |
| SSL Certificate Expiry | < 30 days | < 7 days | Renew immediately |

### 8.3 Logging Standards

```python
# Structured logging format (all services):
{
    "timestamp": "2026-04-10T08:00:00Z",
    "level": "INFO",
    "module": "risk_monitoring.tasks",
    "process": 12345,
    "message": "Risk score computed",
    "user_id": 12345,
    "score": 78.5,
    "request_id": "uuid-here",
    "duration_ms": 45
}
```

### 8.4 Health Check Endpoints

| Endpoint | Purpose | Checks |
|----------|---------|--------|
| `/health/` | ALB health check | App is running |
| `/health/ready/` | Readiness probe | DB + Redis connectivity |
| `/health/live/` | Liveness probe | App process alive |

---

## 9. Incident Response & Rollback

### 9.1 Rollback Procedure

```
SCENARIO: Bad deployment detected

STEP 1: Assess severity
  - P1 (Critical): Data loss, security breach, full outage
  - P2 (Major): Partial outage, feature broken for all users
  - P3 (Minor): Non-critical feature broken, degraded performance

STEP 2: Immediate rollback (< 2 minutes)
  Option A: Re-deploy previous Docker image tag
    aws ecs update-service --force-new-deployment --task-definition <previous>

  Option B: Revert git commit + auto-deploy
    git revert HEAD && git push origin main

STEP 3: If database migration involved
  Option A: Migration is backward-compatible -> rollback code only
  Option B: Migration is destructive -> restore RDS snapshot

STEP 4: Post-incident
  - Verify rollback successful
  - Notify team
  - Write incident report within 24 hours
```

### 9.2 Incident Severity Matrix

| Severity | Response Time | Notify | Example |
|----------|--------------|--------|---------|
| P1 - Critical | Immediate | Entire team, stakeholders | Data breach, full outage |
| P2 - Major | < 30 min | Engineering lead, on-call | API errors > 5%, payments failing |
| P3 - Minor | < 4 hours | Engineering team | Non-critical feature broken |
| P4 - Low | Next business day | Ticket created | UI glitch, minor bug |

---

## 10. Security & Compliance

### 10.1 Security in CI/CD

| Control | Implementation |
|---------|---------------|
| **Secret Detection** | `detect-private-key` pre-commit hook |
| **Dependency Scanning** | Dependabot alerts + auto-PRs |
| **Container Scanning** | ECR image scanning (planned) |
| **SAST** | Ruff security rules (S* prefix) |
| **Branch Protection** | Required reviews, status checks, no force push to main |
| **Signed Commits** | Encouraged (not enforced) |
| **Least Privilege** | ECS tasks use IAM roles, not access keys |

### 10.2 Production Security Hardening

| Setting | Value | Source |
|---------|-------|--------|
| `SECURE_SSL_REDIRECT` | True | `production.py` |
| `SESSION_COOKIE_SECURE` | True | `production.py` |
| `CSRF_COOKIE_SECURE` | True | `production.py` |
| `SECURE_HSTS_SECONDS` | 518400 (target) | `production.py` |
| `SECURE_CONTENT_TYPE_NOSNIFF` | True | `production.py` |
| `X_FRAME_OPTIONS` | DENY | `base.py` |
| `SESSION_COOKIE_HTTPONLY` | True | `base.py` |
| `CSRF_COOKIE_HTTPONLY` | True | `base.py` |
| Password Hashing | Argon2 (primary) | `base.py` |

### 10.3 Compliance Checkpoints

| Checkpoint | Stage | Automated |
|-----------|-------|-----------|
| No secrets in code | Pre-commit | Yes |
| Dependencies CVE-free | PR (Dependabot) | Yes |
| Migrations reviewed | PR review | Manual |
| Access control verified | Staging test | Planned |
| Data encryption at rest | Infrastructure | Yes (RDS, S3) |
| Data encryption in transit | Infrastructure | Yes (TLS everywhere) |
| Audit logging enabled | Application | Yes (EventLog) |
| PII handling compliant | Code review | Manual |

---

## 11. Development Workflow

### 11.1 Branch Strategy

```
main (protected)
  |
  +-- feature/CC-123-add-risk-alerts      (feature branch)
  +-- fix/CC-456-fix-intervention-retry    (bugfix branch)
  +-- hotfix/CC-789-security-patch         (hotfix branch)
```

| Branch Type | Naming | Base | Merge Target | Review Required |
|-------------|--------|------|-------------|----------------|
| Feature | `feature/CC-{ticket}-{desc}` | `main` | `main` | Yes (1+ approver) |
| Bugfix | `fix/CC-{ticket}-{desc}` | `main` | `main` | Yes (1+ approver) |
| Hotfix | `hotfix/CC-{ticket}-{desc}` | `main` | `main` | Yes (expedited) |

### 11.2 Developer Workflow

```
1. Create branch from main
   git checkout -b feature/CC-123-risk-alerts

2. Develop locally
   - Run: python manage.py runserver
   - Test: pytest
   - Lint: pre-commit run --all-files

3. Push and create PR
   git push -u origin feature/CC-123-risk-alerts
   gh pr create

4. CI runs automatically
   - Linter job
   - Pytest job

5. Code review (1+ approval required)

6. Merge to main (squash merge preferred)

7. Auto-deploy to staging

8. Manual promotion to production (after validation)
```

### 11.3 Local Development Setup

```bash
# Clone repository
git clone <repo-url>
cd credit_clear

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Setup local environment
cp .env.example .env  # Edit with local settings

# Setup database
createdb credit_clear
python manage.py migrate

# Install pre-commit hooks
pre-commit install

# Run development server
python manage.py runserver

# Run Celery worker (separate terminal)
celery -A config.celery_app worker -l info

# Run Celery Beat (separate terminal)
celery -A config.celery_app beat -l info

# Run tests
pytest
```

---

## 12. Disaster Recovery

### 12.1 Backup Strategy

| Component | Backup Method | Frequency | Retention |
|-----------|--------------|-----------|-----------|
| Database | RDS Automated Snapshots | Daily | 30 days |
| Database | RDS Manual Snapshot (pre-deploy) | Every deploy | 90 days |
| Media Files | S3 Versioning | Continuous | 90 days |
| Static Files | S3 (reproducible from code) | Every deploy | N/A |
| Secrets | Secrets Manager (versioned) | On change | All versions |
| Code | GitHub (main branch) | Continuous | Indefinite |

### 12.2 Recovery Time Objectives

| Scenario | RTO (Recovery Time) | RPO (Data Loss) |
|----------|-------------------|-----------------|
| Bad deployment | < 5 minutes | Zero |
| Single service failure | < 2 minutes (auto-heal) | Zero |
| Database failure | < 15 minutes (Multi-AZ failover) | Zero |
| Full region failure | < 4 hours | < 1 hour |
| Data corruption | < 1 hour (snapshot restore) | < 24 hours |

### 12.3 Recovery Procedures

| Scenario | Procedure |
|----------|----------|
| **Service crash** | ECS auto-restarts task, ALB reroutes traffic |
| **Bad deploy** | Rollback to previous task definition |
| **DB corruption** | Restore from latest RDS snapshot |
| **Region outage** | Promote read replica in secondary region (DR plan) |
| **Secret compromise** | Rotate all secrets, redeploy all services |

---

*Infrastructure specifications subject to change during active development.*
