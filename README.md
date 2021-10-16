[![CircleCI](https://img.shields.io/circleci/build/github/citizenlabsgr/ballotbuddies)](https://circleci.com/gh/citizenlabsgr/ballotbuddies)
[![Coveralls](https://img.shields.io/coveralls/github/citizenlabsgr/ballotbuddies)](https://coveralls.io/github/citizenlabsgr/ballotbuddies)

# Overview

TODO: Describe this project.

This project was generated with [cookiecutter](https://github.com/audreyr/cookiecutter) using [jacebrowning/template-django](https://github.com/jacebrowning/template-django).

# Setup

## Requirements

The following must be installed on your system:

- Make
- Python
- Poetry
- PostgreSQL

To confirm the correct versions are installed:

```
$ make doctor
```

## Setup

Create a database:

```
$ createdb ballotbuddies_dev
```

Install project dependencies:

```
$ make install
```

Run migrations and generate test data:

```
$ make data
```

## Development

Run the application and recompile static files:

```
$ make run
```

Continuously run validation targets:

```
$ make watch
```

or run them individually:

```
$ make check-backend
$ make test-backend-unit
$ make test-backend-integration
$ make test-system
```
