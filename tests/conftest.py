import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Union

import pytest
import responses
from gordo_dataset.data_provider import providers

from gordo.client import Client
from gordo.client.schemas import Machine


@dataclass
class GordoResponse:
    file_name: Optional[str] = field(default=None, repr=False)
    body: Union[str, bytes, Dict] = ""
    json: str = field(init=False, repr=False)
    status: int = 200
    content_type: str = "application/json"
    method: str = "GET"

    def __post_init__(self):
        if self.file_name:
            self.body = self._read_response(self.file_name)

        if self.content_type == "application/json":
            self.json = json.dumps(self.body)

    def _read_response(self, name):
        path = Path(__file__).parent / "responses" / name
        with open(path, "rb") as fd:
            response = fd.read()
        return json.loads(response)


@pytest.fixture(scope="session")
def gordo_responses():
    return {
        "revision": GordoResponse(file_name="revision.json"),
        "model": GordoResponse(file_name="model.json"),
        "model_no_revision": GordoResponse(status=410, file_name="model_no_revision.json"),
        "model_download": GordoResponse(body=b"\x80\x03X\x04\x00\x00\x00testq\x00.", content_type="application/x-tar"),
        "metadata": GordoResponse(file_name="metadata.json"),
        "anomaly": GordoResponse(file_name="anomaly.json", method="POST"),
    }


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
