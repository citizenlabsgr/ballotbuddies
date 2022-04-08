# Michigan Ballot Buddies

An app to help friends hold each other accountable to vote in every election.

[![CircleCI](https://img.shields.io/circleci/build/github/citizenlabsgr/ballotbuddies)](https://circleci.com/gh/citizenlabsgr/ballotbuddies)
[![Coveralls](https://img.shields.io/coveralls/github/citizenlabsgr/ballotbuddies)](https://coveralls.io/github/citizenlabsgr/ballotbuddies)

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

Run the application:

```
$ make run
```

See the [contributor guide](CONTRIBUTING.md) for additional details.
