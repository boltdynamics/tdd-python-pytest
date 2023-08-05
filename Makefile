SHELL = /bin/bash
SHELLFLAGS = -ex

COVERAGE_FAIL_UNDER = 0

check-prerequisites: ## Check if all prerequisites are installed
	@echo "-- $(shell python --version)"
	@echo "-- $(shell poetry --version)"

clean-environment: ## Clean environment - run with caution!!!!!
	pip uninstall -y tdd-python
	rm -rf poetry.lock pyproject.toml
	rm -rf htmlcov .coverage

initialize-poetry: ## Initialize poetry project and install dependencies
	-poetry init -n --name tdd-python \
		--python ^3.9 \
		--description "TDD Python" \
		--author "Prasiddha Bista" \
		--dependency boto3 \
		--dev-dependency pytest \
		--dev-dependency pytest-mock \
		--dev-dependency pytest-cov

	poetry install --no-root

check-packages: ## Check installed dependencies
	poetry show

test: ## Run Python unit tests
	PYTHONPATH=src pytest \
	--cov-config=.coveragerc \
	--cov-fail-under=${COVERAGE_FAIL_UNDER} \
	--cov-report term-missing \
	--cov=src \
	tests/

test-with-coverage: ## Run Python unit tests with coverage
	pytest --cov-config=.coveragerc \
	--cov-report=html \
	--cov-fail-under=${COVERAGE_FAIL_UNDER} \
	--cov-report term-missing \
	--cov=src \
	tests/
