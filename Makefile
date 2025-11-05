.PHONY: help up down build build-server build-client clean logs logs-server logs-client

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

up:  ## Start production services
	docker compose up -d

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

logs:  ## Show logs from all services
	docker compose logs -f

logs-server:  ## Show server logs
	docker compose logs -f server

logs-client:  ## Show client logs
	docker compose logs -f client
