.PHONY: help up up-dev up-infra down build build-server build-client clean check logs logs-server logs-client logs-ollama logs-postgres logs-minio

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

up:  ## Start all production services
	docker compose up -d

up-dev:  ## Start development infrastructure only (Postgres, MinIO, Ollama)
	docker compose up -d postgres minio ollama
	@echo "Waiting for Ollama to be healthy..."
	@docker compose up ollama-setup
	@echo "Infrastructure services started. Run server and client manually for development."

up-infra:  ## Start infrastructure services (alias for up-dev)
	$(MAKE) up-dev

down:  ## Stop all services
	docker compose down

build:  ## Build production images
	docker compose build

build-server:  ## Build server production image
	docker compose build server

build-client:  ## Build client production image
	docker compose build client

clean:  ## Remove all containers, images, and volumes
	docker compose down -v --rmi all
	cd packages/server && make clean
	cd packages/client && make clean

check:  ## Run all checks for both client and server
	@echo "Running server checks..."
	cd packages/server && make check
	@echo "\nRunning client checks..."
	cd packages/client && make check
	@echo "\nAll checks passed!"

logs:  ## Show logs from all services
	docker compose logs -f

logs-server:  ## Show server logs
	docker compose logs -f server

logs-client:  ## Show client logs
	docker compose logs -f client

logs-ollama:  ## Show Ollama logs
	docker compose logs -f ollama

logs-postgres:  ## Show Postgres logs
	docker compose logs -f postgres

logs-minio:  ## Show MinIO logs
	docker compose logs -f minio
