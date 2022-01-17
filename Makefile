.DEFAULT_GOAL := test

NAME=coffee_juice
VENV_PATH ?= .venv

ifeq ($(OS), Windows_NT)
	VENV_BIN = $(VENV_PATH)/Scripts
	PYTHON_BIN = python
else
	VENV_BIN = $(VENV_PATH)/bin
	PYTHON_BIN = python3.9
endif

PATH := $(VENV_BIN):$(PATH)
VENV_ACTIVATE = . $(VENV_BIN)/activate
PYTHON = $(VENV_BIN)/python
BROWSER := $(PYTHON) -c "import os,sys,webbrowser;webbrowser.open('file://' + os.path.realpath(sys.argv[1]))"

.PHONY: clean
clean: clean-pyc clean-test clean-venv clean-docs clean-install clean-mypy ## remove all build, test, coverage and Python artifacts

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .tox/
	rm -rf .pytest_cache/
	rm -rf .cache/

.PHONY: clean-install
clean-install:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: clean-docs
clean-docs:
	rm -rf docs/build
	rm -rf docs/source/$(NAME)*.rst
	rm -rf docs/source/modules.rst

.PHONY: clean-mypy
clean-mypy:
	rm -rf .mypy_cache

.PHONY: clean-venv
clean-venv:  ## Remove virtual environment
	-rm -rf $(VENV_PATH)

$(VENV_PATH):  ## Create a virtual environment
	virtualenv -p python3.9 $@

$(VENV_PATH)/pip-status: pyproject.toml | $(VENV_PATH) ## Install (upgrade) all development requirements
	poetry install
	touch $@

.PHONY: venv  # A shortcut for "$(VENV_PATH)/pip-status"
venv: $(VENV_PATH)/pip-status ## Install (upgrade) all development requirements

.PHONY: flake8
flake8: venv ## flake8
	$(VENV_BIN)/flake8 $(NAME) tests

.PHONY: safety
safety: venv  # checks your installed dependencies for known security vulnerabilities
	$(VENV_BIN)/safety check

.PHONY: mypy
mypy: venv ## static type check
	$(VENV_BIN)/mypy $(NAME)

.PHONY: lint
lint: flake8 mypy safety ## lint

.PHONY: format
format: venv  ## Autoformat code
	$(VENV_BIN)/isort .

.PHONY: help
help:  ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-23s\033[0m %s\n", $$1, $$2}'

