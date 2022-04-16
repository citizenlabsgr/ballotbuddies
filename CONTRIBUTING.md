# For Contributors

## Setup

### Requirements

* Make:
    * Windows: http://mingw.org/download/installer
    * Mac: http://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make
* Python: `$ pyenv install` or `$ asdf install`
* Poetry: https://python-poetry.org/docs/#installation
* PostgreSQL: `$ brew install postgres`
* direnv: https://direnv.net/

See the [Developer-Machine-Setup](https://github.com/citizenlabsgr/ballotbuddies/wiki/Developer-Machine-Setup) wiki for more instructions.

To confirm these system dependencies are configured correctly:

```
$ make doctor
```

### Installation

Install project dependencies into a virtual environment:

```
$ make install
```

### Data

To automatically create test accounts, update `.envrc` with your own voter information and run `direnv allow`. Then, generate new seed data:

```
$ make data
```

## Development Tasks

### Testing

Manually run the tests:

```
$ make test
```

or keep them running on change:

```
$ make dev
```

> In order to have OS X notifications, `brew install terminal-notifier`.

### Static Analysis

Run linters and static analyzers:

```
$ make check
```

## Continuous Integration

The CI server will report overall build status:

```
$ make ci
```
