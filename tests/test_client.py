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


def test_machine(machine):
    assert machine.host == "gordoserver-project-name-gordo-test"


def test_get_revisions(client, mocked_responses, gordo_responses):
    revision = gordo_responses["revision"]
    mocked_responses.add(
        revision.method,
        "https://localhost:443/gordo/v0/gordo-test/revisions",
        body=revision.json,
        status=revision.status,
        content_type=revision.content_type,
    )

    response = client.get_revisions()

    assert response == revision.body


@pytest.mark.parametrize("revision", [None, "1604861479899"])
def test_get_available_machines(revision, client, mocked_responses, gordo_responses):
    if revision is None:
        revision_response = gordo_responses["revision"]
        mocked_responses.add(
            revision_response.method,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
    model = gordo_responses["model"]
    mocked_responses.add(
        model.method,
        "https://localhost:443/gordo/v0/gordo-test/models",
        body=model.json,
        status=model.status,
        content_type=model.content_type,
    )

    response = client.get_available_machines(revision=revision)

    assert response == model.body


def test_get_available_machines_no_revision(client, mocked_responses, gordo_responses):
    revision = "no_revision"
    model = gordo_responses["model_no_revision"]

    mocked_responses.add(
        model.method,
        "https://localhost:443/gordo/v0/gordo-test/models",
        body=model.json,
        status=model.status,
        content_type=model.content_type,
    )

    with pytest.raises(ResourceGone):
        client.get_available_machines(revision=revision)


@pytest.mark.parametrize("revision", [None, "1604861479899"])
def test_get_machine_names(revision, client, mocked_responses, gordo_responses):
    if revision is None:
        revision_response = gordo_responses["revision"]
        mocked_responses.add(
            revision_response.method,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
    model_response = gordo_responses["model"]
    mocked_responses.add(
        model_response.method,
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
def test_download_model(revision, targets, client, mocked_responses, gordo_responses):
    if revision is None:
        revision_response = gordo_responses["revision"]
        mocked_responses.add(
            revision_response.method,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
        model_response = gordo_responses["model"]
        mocked_responses.add(
            model_response.method,
            "https://localhost:443/gordo/v0/gordo-test/models?revision=1604861479899",
            body=model_response.json,
            status=model_response.status,
            content_type=model_response.content_type,
        )
    model_download_response = gordo_responses["model_download"]
    mocked_responses.add(
        model_download_response.method,
        "https://localhost:443/gordo/v0/gordo-test/07136c88-d39f-41f3-af31-369115a9eb3f-9999/download-model",
        body=model_download_response.body,
        status=model_download_response.status,
        content_type=model_download_response.content_type,
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
def test_get_metadata(revision, targets, client, mocked_responses, gordo_responses):
    if revision is None:
        revision_response = gordo_responses["revision"]
        mocked_responses.add(
            revision_response.method,
            "https://localhost:443/gordo/v0/gordo-test/revisions",
            body=revision_response.json,
            status=revision_response.status,
            content_type=revision_response.content_type,
        )
        model_response = gordo_responses["model"]
        mocked_responses.add(
            model_response.method,
            "https://localhost:443/gordo/v0/gordo-test/models?revision=1604861479899",
            body=model_response.json,
            status=model_response.status,
            content_type=model_response.content_type,
        )
    metadata_response = gordo_responses["metadata"]
    mocked_responses.add(
        metadata_response.method,
        "https://localhost:443/gordo/v0/gordo-test/07136c88-d39f-41f3-af31-369115a9eb3f-9999/metadata?revision=1604861479899",
        body=metadata_response.json,
        status=metadata_response.status,
        content_type=metadata_response.content_type,
    )

    response = client.get_metadata(revision=revision, targets=targets)

    assert response == {
        "07136c88-d39f-41f3-af31-369115a9eb3f-9999": Machine(**metadata_response.body["metadata"]).metadata
    }


# @pytest.mark.parametrize(
#     "revision, targets",
#     [
#         # (None, None),
#         ("1604861479899", ["07136c88-d39f-41f3-af31-369115a9eb3f-9999"]),
#     ],
# )
# def test_predict(revision, targets, client, mocked_responses, gordo_responses):
#     end = datetime.now(tz=UTC)
#     start = end - timedelta(days=7)
#
#     if revision is None:
#         mocked_responses.add(
#             responses.GET,
#             "https://localhost:443/gordo/v0/gordo-test/revisions",
#             body=revision_response.json,
#             status=revision_response.status,
#             content_type=revision_response.content_type,
#         )
#         mocked_responses.add(
#             responses.GET,
#             "https://localhost:443/gordo/v0/gordo-test/models?revision=1604861479899",
#             body=model_response.json,
#             status=model_response.status,
#             content_type=model_response.content_type,
#         )
#     mocked_responses.add(
#         responses.GET,
#         "https://localhost:443/gordo/v0/gordo-test/07136c88-d39f-41f3-af31-369115a9eb3f-9999/metadata?revision=1604861479899",
#         body=metadata_response.json,
#         status=metadata_response.status,
#         content_type=metadata_response.content_type,
#     )
#
#     response = client.predict(start=start, end=end, revision=revision, targets=targets)
#     assert response


def test_predict_single_machine(client, mocked_responses, machine, gordo_responses):
    revision = "1604861479899"
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=7)
    anomaly_response = gordo_responses["anomaly"]
    mocked_responses.add(
        anomaly_response.method,
        "https://localhost:443/gordo/v0/gordo-test/gordo-test/anomaly/prediction?format=json&revision=1604861479899",
        body=anomaly_response.json,
        status=anomaly_response.status,
        content_type=anomaly_response.content_type,
    )

    response = client.predict_single_machine(start=start, end=end, revision=revision, machine=machine)

    assert isinstance(response, PredictionResult)
