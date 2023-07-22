SHELL := /bin/bash

.PHONY: venv-init
venv-init:
	python -m venv .venv

.PHONY: venv
venv:
	source .venv/bin/activate

.PHONY: requirements
requirements: venv
	pip freeze > requirements.txt


.PHONY: install
install: venv
	pip install -r requirements.txt