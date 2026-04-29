# TransactBank API

> **Banking Transaction Service** — A Flask-based REST API for managing accounts, transfers, and financial reporting.

[![Jenkins CI](https://img.shields.io/badge/CI-Jenkins-D24939?logo=jenkins&logoColor=white)](#ci-cd-pipeline)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](#docker)
[![SonarQube](https://img.shields.io/badge/Quality-SonarQube-4E9BCD?logo=sonarqube&logoColor=white)](#sonarqube)

---

## Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [CI/CD Pipeline](#cicd-pipeline)
- [Jenkins Configuration](#jenkins-configuration)
- [Docker](#docker)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Jenkins CI/CD Server                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │ Jenkinsfile  │  │Jenkinsfile.cd│  │Jenkinsfile.nightly │ │
│  │   (CI)       │  │   (CD)       │  │  (Regression)      │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘ │
│         │                 │                    │             │
│  ┌──────┴─────────────────┴────────────────────┴───────────┐ │
│  │           Shared Library (vars/)                        │ │
│  │  notifySlack · deployToEnvironment · rollbackDeployment │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │
                    Docker Build & Push
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    ┌─────────┐      ┌──────────┐      ┌──────────┐
    │   Dev   │      │ Staging  │      │   Prod   │
    │  (K8s)  │      │  (K8s)   │      │  (K8s)   │
    └─────────┘      └──────────┘      └──────────┘
```

### Application Stack

| Component          | Technology                      |
|--------------------|---------------------------------|
| **Runtime**        | Python 3.11, Flask 3.0          |
| **Database**       | PostgreSQL 15                   |
| **Cache**          | Redis 7                         |
| **ORM**            | SQLAlchemy 2.0 + Flask-Migrate  |
| **Serialization**  | Marshmallow 3                   |
| **Container**      | Docker (multi-stage build)      |
| **Orchestration**  | Kubernetes + Helm               |
| **CI/CD**          | Jenkins (Declarative Pipelines) |
| **Code Quality**   | SonarQube, flake8, pylint, mypy |
| **Security**       | Bandit, Trivy, OWASP DC, safety|
| **Notifications**  | Slack                           |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Make (optional)

### Local Development

```bash
# Clone the repository
git clone https://github.com/joao-cognition/jenkins_to_gh_actions.git
cd jenkins_to_gh_actions

# Option A: Docker (recommended)
docker-compose up -d
# API available at http://localhost:5000
# PgAdmin at http://localhost:8080

# Option B: Local Python
make install
make dev
```

### Run Tests

```bash
make test             # All tests with coverage
make test-unit        # Unit tests only
make test-integration # Integration tests only
```

---

## API Reference

### Health

| Method | Path            | Description              |
|--------|-----------------|--------------------------|
| GET    | `/health`       | Basic health check       |
| GET    | `/health/ready` | Readiness (DB check)     |

### Accounts

| Method | Path                              | Description            |
|--------|-----------------------------------|------------------------|
| GET    | `/api/v1/accounts`                | List accounts (paginated, filterable) |
| POST   | `/api/v1/accounts`                | Create new account     |
| GET    | `/api/v1/accounts/:id`            | Get account details    |
| PATCH  | `/api/v1/accounts/:id`            | Update account         |
| GET    | `/api/v1/accounts/:id/balance`    | Get current balance    |

### Transactions

| Method | Path                                    | Description            |
|--------|-----------------------------------------|------------------------|
| GET    | `/api/v1/transactions`                  | List transactions      |
| POST   | `/api/v1/transactions`                  | Create transfer        |
| GET    | `/api/v1/transactions/:id`              | Get transaction        |
| POST   | `/api/v1/transactions/:id/reverse`      | Reverse transaction    |

### Reports

| Method | Path                      | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/v1/reports/summary` | Transaction summary      |
| GET    | `/api/v1/reports/daily`   | Daily report             |

---

## CI/CD Pipeline

The project uses **four Jenkins pipelines**, each serving a distinct purpose:

### 1. `Jenkinsfile` — Main CI Pipeline

Triggered on every push and pull request. Runs the full quality gate:

```
Checkout → Setup Python → Quality Checks (parallel) → Unit Tests → Integration Tests
    → SonarQube → Docker Build → Deploy (branch-gated)
```

**Quality Checks (parallel):**
- flake8 (style linting)
- pylint (code analysis)
- mypy (type checking)
- Bandit (security scanning)

**Branch gating:**
- `main` / `develop` / `release/*` → Docker build + push
- `develop` → auto-deploy to dev
- Feature branches → quality checks + tests only

### 2. `Jenkinsfile.cd` — Continuous Delivery

Manually triggered (or by upstream CI). Handles:
- Production approval gates (requires `release-managers` group)
- Image verification with Trivy
- Database migrations
- Blue/green Kubernetes deployment
- Automated smoke tests with rollback on failure
- Datadog deployment events

### 3. `Jenkinsfile.nightly` — Nightly Regression

Runs at **2:00 AM UTC** daily via cron trigger:
- Full regression test suite (80% coverage threshold)
- Dependency audit (`pip-audit`, `safety`)
- OWASP Dependency Check
- Performance baseline (load test)
- License compliance check

### 4. `Jenkinsfile.release` — Release Pipeline

Manually triggered by release managers:
- Semantic version calculation (patch/minor/major)
- Changelog generation
- Git tagging and pushing
- Docker image promotion (dev tag → `vX.Y.Z`)
- GitHub Release creation
- Optional auto-deploy to production

---

## Jenkins Configuration

### Required Plugins

See [`config/jenkins-credentials.md`](config/jenkins-credentials.md) for the full list of required plugins and credentials.

### Shared Library

The project uses a Jenkins Shared Library (`jenkins/shared-library/vars/`) with these reusable steps:

| Step                    | Description                                     |
|-------------------------|-------------------------------------------------|
| `notifySlack`           | Send formatted Slack notifications              |
| `deployToEnvironment`   | Deploy to a Kubernetes environment              |
| `rollbackDeployment`    | Roll back a failed deployment                   |
| `getEnvironmentUrl`     | Resolve environment-specific URLs               |
| `withPythonVenv`        | Execute commands inside a Python virtualenv      |

**Setup in Jenkins:**
1. Go to **Manage Jenkins → Configure System → Global Pipeline Libraries**
2. Add library with name `transactbank-shared-lib`
3. Point to this repository's `jenkins/shared-library/` directory

### Jenkins Job Configuration

Create four pipeline jobs, one for each Jenkinsfile:

| Job Name              | Script Path            | Trigger                |
|-----------------------|------------------------|------------------------|
| TransactBank-CI       | `Jenkinsfile`          | SCM polling + webhook  |
| TransactBank-CD       | `Jenkinsfile.cd`       | Manual / upstream      |
| TransactBank-Nightly  | `Jenkinsfile.nightly`  | Cron (`H 2 * * *`)    |
| TransactBank-Release  | `Jenkinsfile.release`  | Manual only            |

---

## Docker

### Build

```bash
docker build -t transactbank-api:latest .
```

### Run

```bash
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e FLASK_ENV=production \
  transactbank-api:latest
```

### Full Stack (Development)

```bash
docker-compose up -d
```

Services:
- **API**: http://localhost:5000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **PgAdmin**: http://localhost:8080

---

## Testing

```bash
# All tests
make test

# With detailed coverage
pytest tests/ -v --cov=app --cov-report=html

# Just unit tests
make test-unit

# Just integration tests
make test-integration
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_accounts.py     # Account endpoint tests
│   ├── test_transactions.py # Transaction endpoint tests
│   ├── test_health.py       # Health check tests
│   └── test_validators.py   # Utility function tests
└── integration/
    └── test_workflows.py    # End-to-end banking scenarios
```

---

## Project Structure

```
.
├── Jenkinsfile              # Main CI pipeline
├── Jenkinsfile.cd           # Continuous delivery pipeline
├── Jenkinsfile.nightly      # Nightly regression pipeline
├── Jenkinsfile.release      # Release management pipeline
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # Local development stack
├── Makefile                 # Developer convenience commands
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development & CI dependencies
├── sonar-project.properties # SonarQube configuration
├── setup.cfg                # Tool configurations (flake8, pytest, mypy)
├── pyproject.toml           # Project metadata & tool config
├── .pylintrc                # pylint configuration
├── CHANGELOG.md             # Release history
│
├── app/                     # Application source code
│   ├── __init__.py
│   ├── config.py            # Environment configurations
│   ├── extensions.py        # Flask extension initialization
│   ├── factory.py           # Application factory
│   ├── schemas.py           # Marshmallow schemas
│   ├── models/
│   │   ├── account.py       # Account entity
│   │   └── transaction.py   # Transaction entity
│   ├── routes/
│   │   ├── accounts.py      # Account endpoints
│   │   ├── health.py        # Health check endpoints
│   │   ├── reports.py       # Reporting endpoints
│   │   └── transactions.py  # Transaction endpoints
│   ├── services/
│   │   ├── account_service.py    # Account business logic
│   │   └── transaction_service.py # Transaction business logic
│   └── utils/
│       └── validators.py    # Input validation helpers
│
├── tests/                   # Test suite
├── migrations/              # Database migrations (Alembic)
├── kubernetes/              # K8s manifests (deployment, service, HPA, ingress)
├── jenkins/
│   ├── shared-library/
│   │   └── vars/            # Reusable pipeline steps (Groovy)
│   ├── scripts/             # CI/CD helper scripts
│   └── docker/              # Docker Compose for CI testing
├── scripts/                 # Database initialization scripts
├── config/                  # Documentation (credentials, etc.)
└── docs/                    # Additional documentation
```

---

## License

MIT
