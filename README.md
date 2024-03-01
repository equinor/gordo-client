[![SCM Compliance](https://scm-compliance-api.radix.equinor.com/repos/equinor/117c00d4-fc77-4406-8e47-e616d0d84b62/badge)](https://scm-compliance-api.radix.equinor.com/repos/equinor/117c00d4-fc77-4406-8e47-e616d0d84b62/badge)

# Gordo client

# Table of Contents
* [Installation](#Installation)
* [Developers Instructions](#Developers-Instructions)
	* [Setup](#Setup)
	* [Pre-commit](#Pre-commit)
	* [Run tests](#Run-tests)
* [Contributing](#Contributing)

---

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

## Contributing
We welcome contributions to this project! To get started, please follow these steps:

1. Fork this repository to your own GitHub account and then clone it to your local device.

```
git clone https://github.com/your-account/your-project.git
```

2. Create a new branch for your feature or bug fix.

```
git checkout -b your-feature-or-bugfix-branch
```

3. Make your changes and commit them with a descriptive message.

```
git commit -m "Add a new feature" -a
```

4. Push your changes to your forked repository.

```
git push origin your-feature-or-bugfix-branch
```

5. Open a pull request in this repository and describe the changes you made.

We'll review your changes and work with you to get them merged into the main branch of the project.