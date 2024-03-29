PYTHON_GLOBAL = python3
VENV = venv/bin/
PYTHON = $(VENV)python
PIP = $(VENV)pip
GIT = git

.PHONY: install run

# utils aliases
install: create-venv upgrade-pip install-requirements

# utils
run:
	@$(PYTHON) main.py

create-venv:
	$(info Creating virtual environment...)
	@$(PYTHON_GLOBAL) -m venv venv

upgrade-pip:
	$(info Upgrading pip...)
	@$(PIP) install --upgrade pip

install-requirements:
	$(info Installing requirements...)
	@$(PIP) install -r requirements/development.txt

# requirements
build-dev-requirements:
	$(info Building development requirements...)
	@$(VENV)pip-compile requirements/development.in -o requirements/development.txt

build-production-requirements:
	$(info Building production requirements...)
	@$(VENV)pip-compile requirements/base.in -o requirements/production.txt

build-test-requirements:
	$(info Building test requirements...)
	@$(VENV)pip-compile requirements/test.in -o requirements/test.txt

install-development-requirements:
	$(info Installing development requirements...)
	@$(PIP) install -r requirements/development.txt

install-production-requirements:
	$(info Installing production requirements...)
	@$(PIP) install -r requirements/development.txt

install-test-requirements:
	$(info Installing test requirements...)
	@$(PIP) install -r requirements/test.txt

# requirements aliases
build-requirements: build-dev-requirements build-production-requirements build-test-requirements
dev-requirements: build-dev-requirements install-development-requirements
prod-requirements: build-production-requirements install-production-requirements
test-requirements: build-test-requirements install-test-requirements

