# =============================================================================
# TransactBank API — Development Makefile
# =============================================================================

.PHONY: help install dev test lint typecheck security docker-build docker-up \
        docker-down clean db-upgrade db-migrate seed

PYTHON      ?= python3
VENV        := .venv
BIN         := $(VENV)/bin
APP_NAME    := transactbank-api
DOCKER_TAG  ?= latest

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Python Environment ---

install: ## Create venv and install all dependencies
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip setuptools wheel
	$(BIN)/pip install -r requirements.txt -r requirements-dev.txt

dev: ## Run the development server
	FLASK_ENV=development $(BIN)/python wsgi.py

# --- Quality ---

lint: ## Run all linters (flake8, pylint)
	$(BIN)/flake8 app/ tests/
	$(BIN)/pylint app/ --rcfile=.pylintrc || true

typecheck: ## Run mypy type checker
	$(BIN)/mypy app/ --ignore-missing-imports

security: ## Run security scans (bandit, safety)
	$(BIN)/bandit -r app/ --severity-level medium
	$(BIN)/safety check || true

# --- Testing ---

test: ## Run all tests with coverage
	FLASK_ENV=testing DATABASE_URL="sqlite:///test.db" \
	$(BIN)/pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=75

test-unit: ## Run unit tests only
	FLASK_ENV=testing DATABASE_URL="sqlite:///test.db" \
	$(BIN)/pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests only
	FLASK_ENV=testing DATABASE_URL="sqlite:///test.db" \
	$(BIN)/pytest tests/integration/ -v --tb=short

# --- Database ---

db-upgrade: ## Apply database migrations
	FLASK_ENV=development $(BIN)/flask db upgrade

db-migrate: ## Generate a new migration
	FLASK_ENV=development $(BIN)/flask db migrate -m "$(MSG)"

seed: ## Seed database with test data
	FLASK_ENV=development $(BIN)/python jenkins/scripts/seed_test_data.py

# --- Docker ---

docker-build: ## Build Docker image
	docker build -t $(APP_NAME):$(DOCKER_TAG) .

docker-up: ## Start full stack with docker-compose
	docker-compose up -d

docker-down: ## Stop and remove all containers
	docker-compose down -v

docker-test: ## Run tests inside Docker
	docker-compose -f jenkins/docker/docker-compose.jenkins.yml up -d
	docker-compose -f jenkins/docker/docker-compose.jenkins.yml \
		exec api-test pytest tests/ -v
	docker-compose -f jenkins/docker/docker-compose.jenkins.yml down -v

# --- Cleanup ---

clean: ## Remove build artifacts and caches
	rm -rf $(VENV) .pytest_cache .mypy_cache reports/ *.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
