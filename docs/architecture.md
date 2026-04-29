# TransactBank API — Architecture Decision Records

## ADR-001: Flask over Django

**Status:** Accepted  
**Date:** 2024-02-01

### Context
The v1.x application was built on Django REST Framework. While powerful, the framework imposed overhead for our simple CRUD-focused API. The team needed finer control over middleware, serialization, and database interactions.

### Decision
Migrate to Flask with SQLAlchemy, Marshmallow, and explicit Blueprints.

### Consequences
- Smaller dependency footprint
- More explicit routing and middleware configuration
- Team must manage migrations (Flask-Migrate/Alembic) separately
- Lost Django admin panel (replaced with PgAdmin in docker-compose)

---

## ADR-002: Jenkins Declarative Pipelines

**Status:** Accepted  
**Date:** 2024-02-01

### Context
The team was using freestyle Jenkins jobs configured through the UI. This made pipeline changes hard to track, review, and reproduce.

### Decision
Move to Jenkinsfile-based declarative pipelines stored in the repository.

### Consequences
- Pipeline is version-controlled alongside application code
- Changes require PR review (same as application code)
- Jenkins shared library provides reusable steps
- Requires Jenkins administrators to configure the shared library

---

## ADR-003: Blue/Green Deployment Strategy

**Status:** Accepted  
**Date:** 2024-08-22

### Context
Rolling updates caused brief periods where old and new versions served traffic simultaneously, which is problematic for database-migration-dependent changes.

### Decision
Implement blue/green deployment in `Jenkinsfile.cd` with automated smoke tests and rollback.

### Consequences
- Zero-downtime deployments
- Instant rollback capability
- Double the Kubernetes resources during deployment windows
- More complex deployment pipeline logic

---

## ADR-004: SonarQube Quality Gate as Pipeline Blocker

**Status:** Accepted  
**Date:** 2024-11-10

### Context
Code quality was inconsistent across the team. Static analysis tools (flake8, pylint) ran but did not block merges.

### Decision
Integrate SonarQube analysis into the main CI pipeline and use `waitForQualityGate` to abort builds that fail the quality gate.

### Consequences
- Consistent code quality enforcement
- Requires SonarQube server (maintenance burden)
- May slow down CI pipeline by 1-2 minutes
- Quality gate rules must be carefully tuned to avoid blocking valid changes

---

## ADR-005: Nightly Builds for Security and Compliance

**Status:** Accepted  
**Date:** 2024-11-10

### Context
Security scanning (OWASP, Trivy) and dependency auditing were only run manually. License compliance was never checked.

### Decision
Create a dedicated nightly Jenkins pipeline (`Jenkinsfile.nightly`) that runs the full regression suite plus security and compliance checks.

### Consequences
- Daily visibility into security posture
- License violations caught automatically
- Performance baselines tracked over time
- Requires nightly email/Slack notifications to avoid alert fatigue
