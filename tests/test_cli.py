import pytest
from click.testing import CliRunner

from gordo.client.cli.client import gordo_client


@pytest.fixture
def runner():
    return CliRunner()


def test_subcommands():
    subcommnds = sorted(gordo_client.commands.keys())
    assert subcommnds == ["download-model", "metadata", "predict"]


def test_version(runner):
    result = runner.invoke(gordo_client, ["--version"])

    assert result.exit_code == 0
    assert result.output.startswith("gordo-client, version")
