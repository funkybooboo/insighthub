.PHONY: help dev dev-server dev-client up down check check-server check-client build build-server build-client clean logs

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev:  ## Start all development services
	docker compose --profile dev up

dev-server:  ## Start only server in development mode
	docker compose --profile dev up server-dev

dev-client:  ## Start only client in development mode
	docker compose --profile dev up client-dev

up:  ## Start production services
	docker compose up -d

down:  ## Stop all services
	docker compose down

check:  ## Run quality checks on both packages
	docker compose --profile check build server-check client-check
	@echo "All quality checks passed!"

check-server:  ## Run quality checks on server
	docker compose --profile check build server-check
	@echo "Server quality checks passed!"

check-client:  ## Run quality checks on client
	docker compose --profile check build client-check
	@echo "Client quality checks passed!"

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

logs:  ## Show logs from all services
	docker compose logs -f

logs-server:  ## Show server logs
	docker compose logs -f server

logs-client:  ## Show client logs
	docker compose logs -f client
