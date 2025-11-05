.PHONY: install dev build lint format format-check test clean help

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	bun install

dev:  ## Run development server
	bun run dev

build:  ## Build for production
	bun run build

lint:  ## Run ESLint
	bun run lint

format:  ## Format code with Prettier
	bun run format

format-check:  ## Check if code is formatted
	bun run format:check

test:  ## Run tests
	bun test

check: format-check lint build  ## Run all checks (format, lint, build)

clean:  ## Clean generated files
	rm -rf node_modules dist .vite
	find . -type f -name "*.log" -delete

preview:  ## Preview production build
	bun run preview
