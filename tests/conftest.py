"""Common test code and fixtures."""

import logging

import docker
import pytest
import responses
from gordo_dataset.data_provider import providers
from gordo_dataset.sensor_tag import SensorTag, to_list_of_strings

from gordo.client import Client
from gordo.client.schemas import Machine
from tests.utils import InfluxDB, wait_for_influx

logger = logging.getLogger(__name__)


@pytest.fixture
def machine():
    gordo_test_machine = {
        "name": "gordo-test",
        "dataset": {
            "target_tag_list": ["TRC1", "TRC2"],
            "data_provider": {"min_size": 100, "max_size": 300, "type": "RandomDataProvider"},
            "resolution": "10T",
            "row_filter": "",
            "known_filter_periods": [],
            "aggregation_methods": "mean",
            "row_filter_buffer_size": 0,
            "asset": None,
            "default_asset": None,
            "n_samples_threshold": 0,
            "low_threshold": -1000,
            "high_threshold": 50000,
            "interpolation_method": "linear_interpolation",
            "interpolation_limit": "8H",
            "filter_periods": {},
            "tag_normalizer": "default",
            "train_start_date": "2015-01-01T00:00:00+00:00",
            "train_end_date": "2015-06-01T00:00:00+00:00",
            "tag_list": ["TRC1", "TRC2"],
            "type": "RandomDataset",
        },
        "model": {"sklearn.decomposition.PCA": {"svd_solver": "auto"}},
        "metadata": {
            "user_defined": {},
            "build_metadata": {
                "model": {
                    "model_offset": 0,
                    "model_creation_date": None,
                    "model_builder_version": "1.1.0",
                    "cross_validation": {"scores": {}, "cv_duration_sec": None, "splits": {}},
                    "model_training_duration_sec": None,
                    "model_meta": {},
                },
                "dataset": {"query_duration_sec": None, "dataset_meta": {}},
            },
        },
        "runtime": {"reporters": []},
        "project_name": "project-name",
        "evaluation": {"cv_mode": "full_build"},
    }
    return Machine(**gordo_test_machine)


@pytest.fixture
def client():
    data_provider = providers.RandomDataProvider(min_size=10)
    client = Client(project="gordo-test", data_provider=data_provider)
    return client


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope="session")
def sensors():
    return [SensorTag(f"tag-{i}", None) for i in range(4)]


@pytest.fixture(scope="session")
def sensors_str(sensors):
    return to_list_of_strings(sensors)


@pytest.fixture(scope="session")
def influxdb_name():
    return "testdb"


@pytest.fixture(scope="session")
def influxdb_user():
    return "root"


@pytest.fixture(scope="session")
def influxdb_password():
    return "root"


@pytest.fixture(scope="session")
def influxdb_measurement():
    return "sensors"


@pytest.fixture(scope="session")
def influxdb_fixture_args(sensors_str, influxdb_name, influxdb_user, influxdb_password):
    return (sensors_str, influxdb_name, influxdb_user, influxdb_password, sensors_str)


@pytest.fixture(scope="session")
def influxdb_uri(influxdb_user, influxdb_password, influxdb_name):
    return f"{influxdb_user}:{influxdb_password}@localhost:8086/{influxdb_name}"


@pytest.fixture(scope="session")
def base_influxdb(sensors, influxdb_name, influxdb_user, influxdb_password, influxdb_measurement):
    """
    Fixture to yield a running influx container and pass a tests.utils.InfluxDB
    object which can be used to reset the db to it's original data state.
    """
    client = docker.from_env()

    logger.info("Starting up influx!")
    influx = None
    try:
        influx = client.containers.run(
            image="influxdb:1.7-alpine",
            environment={
                "INFLUXDB_DB": influxdb_name,
                "INFLUXDB_ADMIN_USER": influxdb_user,
                "INFLUXDB_ADMIN_PASSWORD": influxdb_password,
            },
            ports={"8086/tcp": "8086"},
            remove=True,
            detach=True,
        )
        if not wait_for_influx(influx_host="localhost:8086"):
            raise TimeoutError("Influx failed to start")

        logger.info(f"Started influx DB: {influx.name}")

        # Create the interface to the running instance, set default state, and yield it.
        db = InfluxDB(
            sensors,
            influxdb_name,
            influxdb_user,
            influxdb_password,
            influxdb_measurement,
        )
        db.reset()
        logger.info("STARTED INFLUX INSTANCE")
        yield db

    finally:
        logger.info("Killing influx container")
        if influx:
            influx.kill()
        logger.info("Killed influx container")


@pytest.fixture
def influxdb(base_influxdb):
    """
    Fixture to take a running influx and do a reset after each test to ensure
    the data state is the same for each test.
    """
    logger.info("DOING A RESET ON INFLUX DATA")
    base_influxdb.reset()
