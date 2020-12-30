# Gordo client
Client for [Gordo](https://github.com/equinor/gordo) project.

# Table of Contents
* [Installation.](#Installation)
* [Development Tools.](#Development-Tools)
    * [Setup.](#Setup)
        * [Setup Virtual Environment.](#Setup-Virtual-Environment)
    * [Automated Tasks.](#Automated-Tasks)
    
# Installation
In order to install or uninstall this library run following commands.
```bash
# Install
pip install gordo.client

# Uninstall
pip uninstall gordo.client
```
After installation client can be accessed as a library or by command line.
```bash
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

### Development Tools.

#### Setup.
We use [invoke](http://www.pyinvoke.org/) and 
[poetry](https://python-poetry.org/) to speed up the development.

You need to install them only once.

The simplest way to get both is to install [poetry](https://python-poetry.org/)
first, with the officially recommended way:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```
You may need to run following command then:
```
echo 'export PATH="$PATH:$HOME/.poetry/bin"' >> $HOME/.zshrc
```

(Check out alternative instructions for `poetry` installation 
[here](https://python-poetry.org/docs/#installation))

After that [poetry](https://python-poetry.org/) is able to automatically
provide you with `invoke` installed in the project virtual env.  So you can
do one of following [task](#Automated-Tasks):
```
# Run it directly
poetry run inv [task]

# Run it from the virtual environment
poetry shell
inv [task]

# Have an alias (use custom name to avoid clashing with `inv` and `invoke`)
alias invv='poetry run inv'
invv [task]
```

An alternative way to install all tools is using 
[pipx](https://pipxproject.github.io/pipx/):

```
python3.7 -m pip install pipx --user
pipx install poetry
pipx install invoke
```
##### Setup Virtual Environment.
Run `poetry install` to install or re-install all dependencies.

Run `poetry update` to update the locked dependencies to the most recent
version, honoring the constrains put inside `pyproject.toml`.


#### Automated Tasks.
[invoke](http://www.pyinvoke.org/) is used to run some common tasks.
Run one of these from the root of the project.

```
inv fmt       # Apply automatic code formatting.
inv check     # Run static checks.
inv test      # Run tests.
```

The tasks may be chained as following: `inv fmt check test`.

The tasks are defined in [tasks.py](./tasks.py) file.
Run `inv -l` to see a list of all available tasks.
