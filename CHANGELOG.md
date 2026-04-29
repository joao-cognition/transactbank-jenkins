# Changelog

All notable changes to the TransactBank API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.1] - 2025-03-15

### Fixed
- Rate limiter now correctly resets per-client counters on Redis flush
- Fixed decimal precision loss in cross-account transfers above $1M

### Security
- Updated `gunicorn` to 23.0.0 (CVE-2024-1135 mitigation)
- Pinned `werkzeug` to address SSRF in debug mode

## [2.4.0] - 2025-02-01

### Added
- Daily transaction report endpoint (`GET /api/v1/reports/daily`)
- Configurable rate limiting per endpoint via environment variables
- Kubernetes HPA manifest for auto-scaling

### Changed
- Migrated from `Flask-RESTful` to plain Blueprint-based routing
- Upgraded SQLAlchemy to 2.0 style queries

### Deprecated
- XML response format will be removed in v3.0.0

## [2.3.0] - 2024-11-10

### Added
- Transaction reversal endpoint (`POST /api/v1/transactions/{id}/reverse`)
- SonarQube integration in Jenkins pipeline
- Nightly build pipeline with OWASP dependency checks

### Fixed
- Pagination returning incorrect `total` count on filtered queries

## [2.2.0] - 2024-08-22

### Added
- Account filtering by type and active status
- Jenkins shared library for reusable pipeline steps
- Blue/green deployment support in Jenkinsfile.cd

### Changed
- Docker base image from `python:3.10` to `python:3.11-slim`

## [2.1.0] - 2024-05-15

### Added
- Health check and readiness probe endpoints
- Marshmallow schema validation
- Integration test suite

### Fixed
- Missing `Content-Type` header on error responses

## [2.0.0] - 2024-02-01

### Added
- Complete rewrite from Django to Flask
- Multi-stage Dockerfile
- Jenkins CI pipeline with Docker agent

### Removed
- Legacy Django-based application
- Heroku deployment support

## [1.0.0] - 2023-06-01

### Added
- Initial release — Django REST Framework API
- Basic account and transaction CRUD
- Heroku deployment via `Procfile`
