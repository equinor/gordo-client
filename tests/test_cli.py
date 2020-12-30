import json
import tempfile

import pytest
from click.testing import CliRunner
from gordo_dataset.data_provider import providers

from gordo.client.cli.client import gordo_client
from gordo.client.cli.custom_types import DataProviderParam


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


@pytest.mark.parametrize(
    "config",
    (
        '{"type": "RandomDataProvider", "max_size": 200}',
        '{"type": "InfluxDataProvider", "measurement": "value"}',
    ),
)
def test_data_provider_click_param(config, sensors_str):
    """
    Test click custom param to load a provider from a string config representation
    """
    expected_provider_type = json.loads(config)["type"]
    provider = DataProviderParam()(config)
    assert isinstance(provider, getattr(providers, expected_provider_type))

    # Should also be able to take a file path with the json
    with tempfile.NamedTemporaryFile(mode="w") as config_file:
        json.dump(json.loads(config), config_file)
        config_file.flush()

        provider = DataProviderParam()(config_file.name)
        assert isinstance(provider, getattr(providers, expected_provider_type))
