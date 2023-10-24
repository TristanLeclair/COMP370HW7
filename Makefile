.ONESHELL:
.PHONY: setup dirs venv install activate clean
.SILENT:install


ACTIVATE_VENV:=. venv/bin/activate

all: setup

setup: dirs venv install

# Environment
venv: requirements.txt
	@python3 -m venv venv

install:
	@echo "Installing python requirements"
	@$(ACTIVATE_VENV)
	@python3 -m pip install -r requirements.txt --quiet 2>&1

activate:
	@$(ACTIVATE_VENV)

clean: venv
	@echo "Cleaning up previous python virtual environment"
	@rm -rf venv
