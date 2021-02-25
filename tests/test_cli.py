import json
import tempfile
from datetime import datetime

import pytest
from click.exceptions import BadParameter
from click.testing import CliRunner
from gordo_dataset.data_provider import providers

from gordo_client.cli.client import gordo_client
from gordo_client.cli.custom_types import DataProviderParam, IsoFormatDateTime


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


@pytest.mark.parametrize(
    "date",
    (
        "2020-01-01",
        "2020-01-01T12:00:00+00:00",
        "2020-01-01T08:00:00.0",
    ),
)
def test_iso_date_click_param(date):
    result = IsoFormatDateTime()(date)
    assert type(result) == datetime


@pytest.mark.parametrize(
    "date",
    (
        "",
        "test",
        "2018-01-02 test",
    ),
)
def test_iso_date_click_param_not_date(date):
    with pytest.raises(BadParameter):
        IsoFormatDateTime()(date)
