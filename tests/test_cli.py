import pytest
from click.testing import CliRunner

from gordo.client.cli.client import client_cli


@pytest.fixture
def runner():
    return CliRunner()


def test_subcommands():
    subcommnds = sorted(client_cli.commands.keys())
    assert subcommnds == ["download-model", "metadata", "predict"]


def test_version(runner):
    result = runner.invoke(client_cli, ["--version"])

    assert result.exit_code == 0
    assert result.output.startswith("gordo-client, version")
