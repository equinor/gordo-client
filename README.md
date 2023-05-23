# Gordo client
Client for [Gordo](https://github.com/equinor/gordo) project.

[Documentation is available on Read the Docs](https://gordo-client.readthedocs.io/)

## Installation

At least python 3.9 need to be installed in the system first.

In order to install or uninstall this library run following commands.
```bash
# Install
pip install gordo-client

# Uninstall
pip uninstall gordo-client
```

## Developers Instructions

### Setup

Install [poetry](https://python-poetry.org/docs/#installation).

Setup and run development shell instance:

```console
> poetry install
> poetry shell
```

You could also install and apply [pre-commit](https://pre-commit.com/#usage) hooks.

Run `poetry install` to install or re-install all dependencies.

Run `poetry update` to update the locked dependencies to the most recent
version, honoring the constrains put inside `pyproject.toml`.

### Pre-commit

You could also install and apply [pre-commit](https://pre-commit.com/#usage) hooks.

### Run tests

Install [docker](https://docs.docker.com/engine/install/) (or similar container manager) if you want to run test-suite.

Run tests (except docker-related ones):

```console
> poetry run pytest -n auto -m "not dockertest"
```

Run docker-related tests:
```console
> poetry run pytest -m "dockertest"
```
