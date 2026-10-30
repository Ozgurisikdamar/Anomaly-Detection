# StoreGuard developer commands. Phase 0 scaffold.
.DEFAULT_GOAL := help
PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: help setup setup-web setup-mobile lint format typecheck test \
        dev-api dev-web dev-mobile export-mobile-web migrate-sql compose-config

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv and install Python packages (contracts, integrations, vision, api)
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt

setup-web: ## Install web dependencies
	cd apps/web && npm install

setup-mobile: ## Install mobile dependencies
	cd apps/mobile && npm install

lint: ## Ruff (python) + next lint (web)
	.venv/bin/ruff check packages services apps/api
	cd apps/web && npm run lint

format: ## Apply ruff --fix and black
	.venv/bin/ruff check --fix packages services apps/api
	.venv/bin/black packages services apps/api

typecheck: ## mypy (python) + tsc (web, mobile)
	.venv/bin/mypy apps/api/src services/vision/src services/integrations/src packages/contracts/python/src
	cd apps/web && npm run typecheck
	cd apps/mobile && npm run typecheck

test: ## Run the Python test suite
	.venv/bin/pytest apps/api/tests services/integrations/tests services/vision/tests

dev-api: ## Run the API (http://localhost:8000)
	.venv/bin/uvicorn --app-dir apps/api/src storeguard_api.main:app --reload --port 8000

dev-web: ## Run the web dashboard (http://localhost:3000)
	cd apps/web && npm run dev

dev-mobile: ## Run the Expo dev server
	cd apps/mobile && npm run start

export-mobile-web: ## Build the Expo web bundle (static)
	cd apps/mobile && npm run export:web

migrate-sql: ## Emit the initial migration SQL (offline; no DB needed)
	.venv/bin/alembic -c infra/migrations/alembic.ini upgrade head --sql

compose-config: ## Validate docker-compose
	docker compose config >/dev/null && echo "docker-compose OK"
