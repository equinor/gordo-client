import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Union

import pytest
import responses
from pytz import UTC

from gordo.client.io import ResourceGone
from gordo.client.schemas import Machine
from gordo.client.utils import PredictionResult


@dataclass()
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


revision_response = GordoResponse(file_name="revision.json")
model_response = GordoResponse(file_name="model.json")
model_no_revision_responce = GordoResponse(status=410, file_name="model_no_revision.json")
model_download_responce = GordoResponse(body=b"\x80\x03X\x04\x00\x00\x00testq\x00.", content_type="application/x-tar")
metadata_response = GordoResponse(file_name="metadata.json")
anomaly_response = GordoResponse(file_name="anomaly.json", method="POST")


def test_machine(machine):
    assert machine.host == "gordoserver-project-name-gordo-test"


def test_get_revisions(client, mocked_responses):
    mocked_responses.add(
        responses.GET,
        "https://localhost:443/gordo/v0/gordo-test/revisions",
        body=revision_response.json,
        status=revision_response.status,
        content_type=revision_response.content_type,
    )

    response = client.get_revisions()

    assert response == revision_response.body


@pytest.mark.parametrize("revision", [None, "1604861479899"])
def test_get_available_machines(revision, client, mocked_responses):
    if revision is None:
        mocked_responses.add(
            responses.GET,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
    mocked_responses.add(
        responses.GET,
        "https://localhost:443/gordo/v0/gordo-test/models",
        body=model_response.json,
        status=model_response.status,
        content_type=model_response.content_type,
    )

    response = client.get_available_machines(revision=revision)

    assert response == model_response.body


def test_get_available_machines_no_revision(client, mocked_responses):
    revision = "no_revision"
    mocked_responses.add(
        responses.GET,
        "https://localhost:443/gordo/v0/gordo-test/models",
        body=model_no_revision_responce.json,
        status=model_no_revision_responce.status,
        content_type=model_no_revision_responce.content_type,
    )

    with pytest.raises(ResourceGone):
        client.get_available_machines(revision=revision)


@pytest.mark.parametrize("revision", [None, "1604861479899"])
def test_get_machine_names(revision, client, mocked_responses):
    if revision is None:
        mocked_responses.add(
            responses.GET,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
    mocked_responses.add(
        responses.GET,
        "https://localhost:443/gordo/v0/gordo-test/models",
        body=model_response.json,
        status=model_response.status,
        content_type=model_response.content_type,
    )

    response = client.get_machine_names(revision=revision)

    assert response == model_response.body["models"]


@pytest.mark.parametrize(
    "revision, targets",
    [
        (None, None),
        ("1604861479899", ["07136c88-d39f-41f3-af31-369115a9eb3f-9999"]),
    ],
)
def test_download_model(revision, targets, client, mocked_responses):
    if revision is None:
        mocked_responses.add(
            responses.GET,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
        mocked_responses.add(
            responses.GET,
            "https://localhost:443/gordo/v0/gordo-test/models?revision=1604861479899",
            body=model_response.json,
            status=model_response.status,
            content_type=model_response.content_type,
        )
    mocked_responses.add(
        responses.GET,
        "https://localhost:443/gordo/v0/gordo-test/07136c88-d39f-41f3-af31-369115a9eb3f-9999/download-model",
        body=model_download_responce.body,
        status=model_download_responce.status,
        content_type=model_download_responce.content_type,
    )

    response = client.download_model(revision=revision, targets=targets)

    assert response == {
        "07136c88-d39f-41f3-af31-369115a9eb3f-9999": "test",
    }


@pytest.mark.parametrize(
    "revision, targets",
    [
        (None, None),
        ("1604861479899", ["07136c88-d39f-41f3-af31-369115a9eb3f-9999"]),
    ],
)
def test_get_metadata(revision, targets, client, mocked_responses):
    if revision is None:
        mocked_responses.add(
            responses.GET,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
        mocked_responses.add(
            responses.GET,
            "https://localhost:443/gordo/v0/gordo-test/models?revision=1604861479899",
            body=model_response.json,
            status=model_response.status,
            content_type=model_response.content_type,
        )
    mocked_responses.add(
        responses.GET,
        "https://localhost:443/gordo/v0/gordo-test/07136c88-d39f-41f3-af31-369115a9eb3f-9999/metadata?revision=1604861479899",
        body=metadata_response.json,
        status=metadata_response.status,
        content_type=metadata_response.content_type,
    )

    response = client.get_metadata(revision=revision, targets=targets)

    assert response == {
        "07136c88-d39f-41f3-af31-369115a9eb3f-9999": Machine(**metadata_response.body["metadata"]).metadata
    }


def test_predict_single_machine(client, mocked_responses, machine):
    revision = "1604861479899"
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=7)

    mocked_responses.add(
        anomaly_response.method,
        "https://localhost:443/gordo/v0/gordo-test/gordo-test/anomaly/prediction?format=json&revision=1604861479899",
        body=anomaly_response.json,
        status=anomaly_response.status,
        content_type=anomaly_response.content_type,
    )

    response = client.predict_single_machine(start=start, end=end, revision=revision, machine=machine)

    assert isinstance(response, PredictionResult)
