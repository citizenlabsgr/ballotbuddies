ifdef CIRCLECI
	RUN := poetry run
else ifdef HEROKU_APP_NAME
	SKIP_INSTALL := true
else
	RUN := poetry run
endif

.PHONY: all
all: check test ## CI | Run all validation targets

.PHONY: dev
dev: install ## CI | Rerun all validation targests in a loop
	@ rm -rf $(FAILURES)
	$(RUN) sniffer

# SYSTEM DEPENDENCIES #########################################################

.PHONY: bootstrap
bootstrap: ## Attempt to install system dependencies
	asdf plugin add python || asdf plugin update python
	asdf plugin add poetry https://github.com/asdf-community/asdf-poetry.git || asdf plugin update poetry
	asdf install

.PHONY: doctor
doctor: ## Check for required system dependencies
	bin/verchew-wrapper --exit-code

.envrc:
	echo export SECRET_KEY=local >> $@
	echo export DATABASE_URL=postgresql://localhost/ballotbuddies_dev >> $@
	echo export REDIS_URL=redis://127.0.0.1:6379/0 >> $@
	echo >> $@
	echo export MANDRILL_API_KEY=??? >> $@
	echo >> $@
	echo export ELECTIONS_HOST=https://michiganelections.io >> $@
	echo export PREVIEW_HOST=https://share.michiganelections.io >> $@
	echo export TEST_VOTERS=you@yourdomain.com,First,Last,YYYY-MM-DD,ZIP/test@example.com,Rosalynn,Bliss,1975-08-03,49503 >> $@
	- direnv allow

# PROJECT DEPENDENCIES ########################################################

VIRTUAL_ENV ?= .venv

BACKEND_DEPENDENCIES = $(VIRTUAL_ENV)/.poetry-$(shell bin/checksum pyproject.toml poetry.lock)

.PHONY: install
ifndef SKIP_INSTALL
install: $(BACKEND_DEPENDENCIES) ## Install project dependencies
endif

$(BACKEND_DEPENDENCIES): poetry.lock
	@ rm -rf $(VIRTUAL_ENV)/.poetry-*
	@ rm -rf ~/Library/Preferences/pypoetry
	@ poetry config virtualenvs.in-project true
	poetry install
	@ mkdir -p staticfiles
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock --no-update
	@ touch $@
endif

.PHONY: clean
clean:
	rm -rf .cache .coverage htmlcov staticfiles

.PHONY: clean-all
clean-all: clean
	rm -rf $(VIRTUAL_ENV)

# RUNTIME DEPENDENCIES ########################################################

.PHONY: migrations
migrations: install  ## Database | Generate database migrations
	$(RUN) python manage.py makemigrations

.PHONY: migrate
migrate: install ## Database | Run database migrations
	$(RUN) python manage.py migrate

.PHONY: data
data: install migrate ## Database | Seed data for manual testing
	$(RUN) python manage.py gendata $(TEST_VOTERS)

.PHONY: reset
reset: install ## Database | Create a new database, migrate, and seed it
	- dropdb ballotbuddies_dev
	- createdb ballotbuddies_dev
	make data

# VALIDATION TARGETS ##########################################################

PYTHON_PACKAGES := config ballotbuddies
FAILURES := .cache/pytest/v/cache/lastfailed

.PHONY: check
check: check-backend ## Run static analysis

.PHONY: format
format: format-backend

.PHONY: check-backend
check-backend: install format-backend
	$(RUN) mypy $(PYTHON_PACKAGES) tests
	$(RUN) pylint $(PYTHON_PACKAGES) tests --rcfile=.pylint.ini

format-backend: install
	$(RUN) isort $(PYTHON_PACKAGES) tests
	$(RUN) black $(PYTHON_PACKAGES) tests

ifdef DISABLE_COVERAGE
PYTEST_OPTIONS := --no-cov --disable-warnings
endif

.PHONY: test
test: test-backend ## Run all tests

.PHONY: test-backend
test-backend: test-backend-all
ifdef COVERALLS_REPO_TOKEN
	poetry run coveralls
endif

.PHONY: test-backend-unit
test-backend-unit: install
	@ ( mv $(FAILURES) $(FAILURES).bak || true ) > /dev/null 2>&1
	$(RUN) pytest $(PYTHON_PACKAGES) tests/unit -m "not django_db" $(PYTEST_OPTIONS)
	@ ( mv $(FAILURES).bak $(FAILURES) || true ) > /dev/null 2>&1
ifndef DISABLE_COVERAGE
	$(RUN) coveragespace update unit
endif

.PHONY: test-backend-integration
test-backend-integration: install
	@ if test -e $(FAILURES); then $(RUN) pytest tests/integration; fi
	@ rm -rf $(FAILURES)
	$(RUN) pytest tests/integration $(PYTEST_OPTIONS)
	$(RUN) coveragespace update integration

.PHONY: test-backend-all
test-backend-all: install
	@ if test -e $(FAILURES); then $(RUN) pytest $(PYTHON_PACKAGES) tests/unit tests/integration; fi
	@ rm -rf $(FAILURES)
	$(RUN) pytest $(PYTHON_PACKAGES) tests/unit tests/integration $(PYTEST_OPTIONS)
	$(RUN) coveragespace update overall

.PHONY: test-system
test-system: install
	$(RUN) honcho start --procfile=tests/system/Procfile --env=tests/system/.env

# SERVER TARGETS ##############################################################

.PHONY: run
run: .envrc install migrate ## Run the applicaiton
	$(RUN) python manage.py runserver

.PHONY: run-production
run-production: .envrc install
	poetry run python manage.py collectstatic --no-input
	poetry run heroku local release
	HEROKU_APP_NAME=local poetry run heroku local web --port=$${PORT:-8000}

# RELEASE TARGETS #############################################################

.PHONY: build
build: install

.PHONY: deploy
deploy:
	@ echo
	git diff --exit-code
	heroku git:remote -a ballotbuddies-staging
	@ echo
	git push heroku main

.PHONY: promote
promote: install
	@ echo
	TEST_SITE=https://staging-app.michiganelections.io $(RUN) pytest tests/system --cache-clear
	@ echo
	heroku pipelines:promote --app ballotbuddies-staging --to ballotbuddies
	@ echo
	TEST_SITE=https://app.michiganelections.io $(RUN) pytest tests/system

# HELP ########################################################################

.PHONY: help
help: install
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
