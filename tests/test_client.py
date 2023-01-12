import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Union

import pytest
from pytz import UTC

from gordo_client.io import BadGordoResponse, ResourceGone
from gordo_client.schemas import Machine
from gordo_client.utils import PredictionResult
from gordo_client import Client


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


gordo_responses = {
    "revision": GordoResponse(file_name="revision.json"),
    "model": GordoResponse(file_name="model.json"),
    "model_no_revision": GordoResponse(status=410, file_name="model_no_revision.json"),
    "model_download": GordoResponse(body=b"\x80\x03X\x04\x00\x00\x00testq\x00.", content_type="application/x-tar"),
    "metadata": GordoResponse(file_name="metadata.json"),
    "anomaly": GordoResponse(file_name="anomaly.json", method="POST"),
}


def _mock_response(mocked_responses, url, response_name):
    client_response = gordo_responses[response_name]
    mocked_responses.add(
        method=client_response.method,
        url=f"https://localhost:443{url}",
        body=client_response.json if client_response.content_type == "application/json" else client_response.body,
        status=client_response.status,
        content_type=client_response.content_type,
    )
    return client_response


def test_bad_gordo_response(client, mocked_responses):
    mocked_responses.add(
        method="GET",
        url="https://localhost:443/gordo/v0/gordo-test/revisions",
        body="<title>Sign in to your account</title>",
        status=200,
        content_type="text/html; charset=utf-8",
    )

    with pytest.raises(BadGordoResponse):
        client.get_revisions()


def test_get_revisions(client, mocked_responses):
    revision_response = _mock_response(mocked_responses, "/gordo/v0/gordo-test/revisions", "revision")

    response = client.get_revisions()

    assert response == revision_response.body


@pytest.mark.parametrize("revision", [None, "1604861479899"])
def test_get_available_machines(revision, client, mocked_responses):
    if revision is None:
        _mock_response(mocked_responses, "/gordo/v0/gordo-test/revisions", "revision")
    model_response = _mock_response(mocked_responses, "/gordo/v0/gordo-test/models", "model")

    response = client.get_available_machines(revision=revision)

    assert response == model_response.body


def test_get_available_machines_no_revision(client, mocked_responses):
    revision = "no_revision"
    _mock_response(mocked_responses, "/gordo/v0/gordo-test/models", "model_no_revision")

    with pytest.raises(ResourceGone):
        client.get_available_machines(revision=revision)


@pytest.mark.parametrize("revision", [None, "1604861479899"])
def test_get_machine_names(revision, client, mocked_responses):
    if revision is None:
        _mock_response(mocked_responses, "/gordo/v0/gordo-test/revisions", "revision")
    model_response = _mock_response(mocked_responses, "/gordo/v0/gordo-test/models", "model")

    response = client.get_machine_names(revision=revision)

    assert response == model_response.body["models"]


@pytest.mark.parametrize(
    "revision, targets", [(None, None), ("1604861479899", ["07136c88-d39f-41f3-af31-369115a9eb3f-9999"])]
)
def test_download_model(revision, targets, client, mocked_responses):
    if revision is None:
        _mock_response(mocked_responses, "/gordo/v0/gordo-test/revisions", "revision")
        _mock_response(mocked_responses, "/gordo/v0/gordo-test/models?revision=1604861479899", "model")
    _mock_response(
        mocked_responses,
        "/gordo/v0/gordo-test/07136c88-d39f-41f3-af31-369115a9eb3f-9999/download-model",
        "model_download",
    )

    response = client.download_model(revision=revision, targets=targets)

    assert response == {"07136c88-d39f-41f3-af31-369115a9eb3f-9999": "test"}


@pytest.mark.parametrize(
    "revision, targets", [(None, None), ("1604861479899", ["07136c88-d39f-41f3-af31-369115a9eb3f-9999"])]
)
def test_get_metadata(revision, targets, client, mocked_responses):
    if revision is None:
        _mock_response(mocked_responses, "/gordo/v0/gordo-test/revisions", "revision")
        _mock_response(mocked_responses, "/gordo/v0/gordo-test/models?revision=1604861479899", "model")
    metadata_response = _mock_response(
        mocked_responses,
        "/gordo/v0/gordo-test/07136c88-d39f-41f3-af31-369115a9eb3f-9999/metadata?revision=1604861479899",
        "metadata",
    )

    response = client.get_metadata(revision=revision, targets=targets)

    assert response == {
        "07136c88-d39f-41f3-af31-369115a9eb3f-9999": Machine(**metadata_response.body["metadata"]).metadata
    }


def test_predict_single_machine(client, mocked_responses, machine):
    revision = "1604861479899"
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=7)
    _mock_response(
        mocked_responses,
        "/gordo/v0/gordo-test/gordo-test/anomaly/prediction?format=json&revision=1604861479899",
        "anomaly",
    )

    response = client.predict_single_machine(start=start, end=end, revision=revision, machine=machine)

    assert isinstance(response, PredictionResult)


def test_predict_single_machine_all_columns(data_provider, mocked_responses, machine):
    client = Client(project="gordo-test", data_provider=data_provider, all_columns=True)

    revision = "1604861479899"
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=7)
    _mock_response(
        mocked_responses,
        "/gordo/v0/gordo-test/gordo-test/anomaly/prediction?format=json&revision=1604861479899&all_columns=true",
        "anomaly",
    )

    response = client.predict_single_machine(start=start, end=end, revision=revision, machine=machine)

    assert isinstance(response, PredictionResult)
