.PHONY: setup clean deploy destroy seed bootstrap synth check-env test-function test lint format run

# Default Python version
PYTHON_VERSION := 3.12
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
CDK := cdk  # Use system CDK
CDK_APP := "$(PYTHON) cdk/app.py"
PRE_COMMIT := $(VENV)/bin/pre-commit

# AWS region (default to us-east-1 if not set)
AWS_REGION ?= us-east-1

# Check if required tools are installed
check-tools:
	@echo "Checking required tools..."
	@command -v aws >/dev/null 2>&1 || { echo "AWS CLI is required but not installed. Visit: https://aws.amazon.com/cli/"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed."; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "npm is required but not installed. Visit: https://nodejs.org/"; exit 1; }
	@command -v cdk >/dev/null 2>&1 || { echo "AWS CDK is required but not installed globally. Installing..."; npm install -g aws-cdk; }

# Create and activate virtual environment
venv: check-tools
	@echo "Creating Python virtual environment..."
	@python3 -m venv $(VENV)
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "Installing pre-commit hooks..."
	@$(PRE_COMMIT) install

# Bootstrap CDK environment
bootstrap: venv
	@echo "Bootstrapping CDK environment..."
	@$(CDK) bootstrap --app $(CDK_APP) aws://$(shell aws sts get-caller-identity --query Account --output text)/$(AWS_REGION)

# Deploy the stack
deploy: check-env
	@echo "Deploying CDK stack..."
	@$(CDK) deploy --app $(CDK_APP) --region $(AWS_REGION)

# Seed the database tables
seed: check-env
	@echo "Seeding DynamoDB tables..."
	@cd scripts && python3 seed_subscriptions.py && python3 seed_products.py && python3 seed_goals.py && python3 seed_function_catalog.py

# Destroy the stack
destroy: check-env
	@echo "Destroying CDK stack..."
	@$(CDK) destroy --app $(CDK_APP) --region $(AWS_REGION)

# Synthesize CloudFormation template
synth: check-env
	@echo "Synthesizing CloudFormation template..."
	@$(CDK) synth --app $(CDK_APP)

# Check if virtual environment exists
check-env:
	@test -d $(VENV) || { echo "Virtual environment not found. Run 'make setup' first."; exit 1; }

# Clean up generated files
clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@rm -rf cdk.out
	@rm -rf .cdk.staging
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

# Run tests
test: check-env
	@echo "Running tests..."
	@pytest

# Run tests with coverage
test-cov: check-env
	@echo "Running tests with coverage..."
	@pytest --cov=cdk --cov-report=term-missing

# Run linting
lint: check-env
	@echo "Running linters..."
	@flake8 cdk tests scripts
	@mypy cdk tests scripts

# Format code
format: check-env
	@echo "Formatting code..."
	@black cdk tests scripts
	@isort cdk tests scripts

# Test function matcher and execution
test-function: check-env
	@echo "Testing function matcher and execution"
	@python3 scripts/test_functions.py "$(prompt)" $(if $(user_id),--user-id $(user_id),) $(if $(skip),--skip-execution,)

# Run the CLI
run: check-env
	@echo "Starting Financial Tools CLI..."
	@$(PYTHON) -m financial_tools.cli

# Main setup target that runs everything
setup: check-tools venv bootstrap deploy seed
	@echo "Setup complete! Your CDK stack is deployed and seeded with initial data."
	@echo "To destroy the stack when done, run: make destroy"
	@echo "To clean up local files, run: make clean"

# Help target
help:
	@echo "Available targets:"
	@echo "  make setup      - Complete setup: create venv, install deps, deploy stack, and seed data"
	@echo "  make deploy     - Deploy the CDK stack"
	@echo "  make destroy    - Destroy the CDK stack"
	@echo "  make seed       - Seed the DynamoDB tables with initial data"
	@echo "  make clean      - Clean up generated files and virtual environment"
	@echo "  make synth      - Synthesize CloudFormation template"
	@echo "  make test       - Run all tests"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make format     - Format code (black, isort)"
	@echo "  make run        - Run the Financial Tools CLI"
	@echo "  make test-function prompt=\"...\" - Test function matcher with a prompt"
	@echo "  make help       - Show this help message"
