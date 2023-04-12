# Gordo client
Client for [Gordo](https://github.com/equinor/gordo) project.

## Table of Contents

* [Installation.](#Installation)
* [Developers Instructions.](#Developers-Instructions)
    * [Setup.](#Setup)
    * [Run tests.](#Run-tests)
    
## Installation

At least python 3.9 need to be installed in the system first.

In order to install or uninstall this library run following commands.
```bash
# Install
pip install gordo-client

# Uninstall
pip uninstall gordo-client
```
After installation client can be accessed as a library or by command line.
```
Usage: gordo-client [OPTIONS] COMMAND [ARGS]...

  Entry sub-command for client related activities.

Options:
  --version                   Show the version and exit.
  --project TEXT              The project to target
  --host TEXT                 The host the server is running on
  --port INTEGER              Port the server is running on
  --scheme TEXT               tcp/http/https
  --batch-size INTEGER        How many samples to send
  --parallelism INTEGER       Maximum asynchronous jobs to run
  --metadata KEY_VALUE_PAR    Key-Value pair to be entered as metadata labels,
                              may use this option multiple times. to be
                              separated by a comma. ie: --metadata key,val
                              --metadata some key,some value
  --session-config SAFE_LOAD  Config json/yaml to set on the requests.Session
                              object. Useful when needing to
                              supplyauthentication parameters such as header
                              keys. ie. --session-config {'headers': {'API-
                              KEY': 'foo-bar'}}
  --help                      Show this message and exit.

Commands:
  download-model  Download the actual model from the target and write to an...
  metadata        Get metadata from a given endpoint.
  predict         Run some predictions against the target.
```

## Developers Instructions

### Setup

Install [poetry](https://python-poetry.org/docs/#installation).

Setup and run development shell instance:

```console
> poetry shell
> poetry install
```

You could also install and apply [pre-commit](https://pre-commit.com/#usage) hooks.

Run `poetry install` to install or re-install all dependencies.

Run `poetry update` to update the locked dependencies to the most recent
version, honoring the constrains put inside `pyproject.toml`.

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
