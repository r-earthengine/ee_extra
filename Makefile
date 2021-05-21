SHELL := /usr/bin/env bash

# Sub-modules
MAIN = **/*.py
IMAGE = **/image/*.py

# 1. Install poetry
.PHONY: download-poetry
download-poetry:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# 2. Upgrade/Install ee_extra
.PHONY: upgrade-poetry
upgrade-poetry:
	poetry lock -n
	poetry install -n

# 3. Check code style black
.PHONY: black
black:
	poetry run black --config pyproject.toml --diff --check ./


# 4. Check documentation
.PHONY: doc
doc:
	poetry run darglint -v 2 ./

# 5. Fix order of Python libraries
.PHONY: isort_fix
isort_fix:
	poetry run isort --settings-path pyproject.toml $(MAIN)
	poetry run isort --settings-path pyproject.toml $(IMAGE)	

# 6. Check order of Python libraries
.PHONY: isort
isort:
	poetry run isort --settings-path pyproject.toml $(MAIN)
	poetry run isort --settings-path pyproject.toml --check-only $(IMAGE)

# 7. Static type checker
.PHONY: mypy
mypy:
	poetry run mypy --config-file setup.cfg ee_extra tests/**/*.py

# 8. Run unit testing
.PHONY: test
test:
	poetry run pytest

# 9. Run lint
.PHONY: lint
lint: test check-safety check-style

# 10. Build package
.PHONY: build
build: 
	poetry build

# 11. Install package
.PHONY: install
install: 
	pip3 install .


# 12. Publish package on pip
.PHONY: publish
publish: 
	poetry build
	poetry publish

# 12. Publish package same version on pip
.PHONY: publish-same
publish-same: 
	poetry publish --dry-run
	twine upload --skip-existing dist/*
