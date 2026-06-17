.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help up down build logs migrate seed backend-test frontend-test test lint backend-lint frontend-lint e2e

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

up: ## Build and start the full stack (api, worker, db, broker, frontend)
	$(COMPOSE) up --build -d
	@echo "API:       http://localhost:8000/docs"
	@echo "Frontend:  http://localhost:5173"
	@echo "RabbitMQ:  http://localhost:15672 (guest/guest)"

down: ## Stop and remove containers
	$(COMPOSE) down

build: ## Build all images
	$(COMPOSE) build

logs: ## Tail logs from all services
	$(COMPOSE) logs -f

migrate: ## Run database migrations inside the backend container
	$(COMPOSE) run --rm backend alembic upgrade head

seed: ## Seed the database with synthetic analyses
	$(COMPOSE) run --rm backend python -m scripts.seed

train: ## Fine-tune a model on your images (DATA=./data OUT=./weights/model.pt)
	$(COMPOSE) run --rm -v $(PWD)/$(DATA):/data/train backend \
		python -m scripts.train --data-dir /data/train --out $(or $(OUT),weights/model.pt)

backend-test: ## Run backend unit tests (pytest)
	cd backend && python -m pytest

frontend-test: ## Run frontend unit tests (vitest)
	cd frontend && npm run test

e2e: ## Run Playwright end-to-end tests (requires the stack running)
	cd frontend && npm run test:e2e

test: backend-test frontend-test ## Run all unit tests

backend-lint: ## Lint backend (ruff)
	cd backend && ruff check app scripts

frontend-lint: ## Lint frontend (eslint)
	cd frontend && npm run lint

lint: backend-lint frontend-lint ## Lint everything
