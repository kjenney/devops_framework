.PHONY: install test lint type-check format clean help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install in editable mode with dev dependencies
	pip install -e ".[dev]"

test:  ## Run all tests
	pytest

test-verbose:  ## Run tests with verbose output
	pytest -v

test-fast:  ## Run tests without coverage
	pytest --no-cov

lint:  ## Run ruff linter
	ruff check src/ tests/

lint-fix:  ## Run ruff linter and auto-fix
	ruff check --fix src/ tests/

format:  ## Format code with ruff
	ruff format src/ tests/

type-check:  ## Run mypy type checker
	mypy src/

clean:  ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info/ src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -f .coverage

smoke-aws:  ## Smoke test AWS CLI
	devops aws list-instances --region us-east-1

smoke-eks:  ## Smoke test EKS CLI
	devops eks list-pods --namespace default

smoke-datadog:  ## Smoke test Datadog CLI
	devops datadog query-metrics --query "avg:system.cpu.user{*}"

docs-serve:  ## Serve documentation locally with live reload
	.venv/bin/mkdocs serve --dev-addr 127.0.0.1:8001

docs-build:  ## Build static documentation site to site/
	.venv/bin/mkdocs build --strict
