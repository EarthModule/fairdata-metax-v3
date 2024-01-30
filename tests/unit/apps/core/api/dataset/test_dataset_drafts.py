import json
import logging
from copy import deepcopy
from unittest.mock import ANY

import pytest
from rest_framework.reverse import reverse
from tests.utils import assert_nested_subdict, matchers

from apps.core import factories
from apps.core.factories import DatasetFactory, MetadataProviderFactory
from apps.core.models import OtherIdentifier
from apps.core.models.catalog_record.dataset import Dataset
from apps.core.models.concepts import IdentifierType
from apps.files.factories import FileStorageFactory

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.django_db, pytest.mark.dataset]


def pop_nested_ids(dataset: dict) -> dict:
    """Remove ids from nested dicts, return id to dict mapping."""
    ids = {}

    def _pop(object):
        if isinstance(object, list):
            object = dict(enumerate(object))
        if isinstance(object, dict):
            if "id" in object:
                obj_id = object.pop("id")
                if not "pref_label" in object:  # ignore refdata
                    ids[obj_id] = object
            for value in object.values():
                _pop(value)

    _pop(dataset)
    return ids


def test_create_draft(admin_client, dataset_a_json, data_catalog, reference_data):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 201
    draft = res.json()

    res = admin_client.get(f"/v3/datasets/{dataset_id}", content_type="application/json")
    assert res.status_code == 200
    original = res.json()

    assert original["state"] == "published"
    assert draft["state"] == "draft"
    assert original["id"] in draft["draft_of"]
    assert draft["id"] in original["next_draft"]
    metadata_owner_id = draft["metadata_owner"]["id"]
    assert draft["metadata_owner"] == original["metadata_owner"]

    # Remove fields that should be different
    for field in [
        "id",
        "state",
        "next_draft",
        "draft_of",
        "next_version",
        "last_version",
        "previous_version",
        "first_version",
        "published_revision",
        "draft_revision",
        "created",
        "modified",
        "persistent_identifier",
    ]:
        original.pop(field)
        draft.pop(field)

    # Nested data should be equal but with different ids (except refdata)
    original_ids = pop_nested_ids(original)
    draft_ids = pop_nested_ids(draft)
    assert original == draft

    # Check that no nested ids are shared
    original_ids.pop(metadata_owner_id)
    draft_ids.pop(metadata_owner_id)
    assert set(original_ids).intersection(draft_ids) == set()


def test_create_draft_from_draft(admin_client, dataset_a_json, data_catalog, reference_data):
    dataset_a_json["state"] = "draft"
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 400
    assert res.json()["state"] == "Dataset needs to be published before creating a new draft."


def test_create_draft_twice(admin_client, dataset_a_json, data_catalog, reference_data):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 201
    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 400
    assert res.json()["next_draft"] == "Dataset already has a draft."


def test_create_draft_by_changing_state(
    admin_client, dataset_a_json, data_catalog, reference_data
):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.patch(
        f"/v3/datasets/{dataset_id}", {"state": "draft"}, content_type="application/json"
    )
    assert res.status_code == 400
    assert res.json()["state"] == "Value cannot be changed directly for an existing dataset."


def test_merge_draft(
    admin_client, dataset_a_json, dataset_maximal_json, data_catalog, reference_data
):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    assert res.data["state"] == "published"
    dataset_id = res.data["id"]

    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 201
    draft_id = res.data["id"]

    dataset_maximal_json.pop("metadata_owner")
    res = admin_client.patch(
        f"/v3/datasets/{draft_id}", dataset_maximal_json, content_type="application/json"
    )
    assert res.status_code == 200
    draft_data = deepcopy(res.json())

    # Merge draft
    res = admin_client.post(f"/v3/datasets/{draft_id}/publish", content_type="application/json")
    assert res.status_code == 200
    merge_data = res.json()  # response should be the updated original dataset

    # Dataset has been updated
    res = admin_client.get(f"/v3/datasets/{dataset_id}", content_type="application/json")
    assert res.status_code == 200

    published_data = deepcopy(res.json())
    assert published_data == merge_data

    # Remove fields that should be different for draft and merged version
    for field in [
        "id",
        "state",
        "published_revision",
        "draft_revision",
        "draft_of",
        "next_draft",
        "created",
    ]:
        draft_data.pop(field)
        published_data.pop(field)
    assert draft_data.pop("persistent_identifier") != published_data.pop("persistent_identifier")

    # Check that data from draft has been moved to published version
    assert_nested_subdict(draft_data, published_data)

    # Draft has been removed
    res = admin_client.get(f"/v3/datasets/{draft_id}", content_type="application/json")
    assert res.status_code == 404


def test_delete_draft(admin_client, dataset_a_json, data_catalog, reference_data):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 201
    draft = res.data
    assert Dataset.all_objects.filter(id=draft["id"]).exists()

    res = admin_client.delete(
        f"/v3/datasets/{draft['id']}", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 204
    assert not Dataset.all_objects.filter(id=draft["id"]).exists()


@pytest.mark.xfail(reason="too many revisions are created")
def test_draft_revisions(admin_client, dataset_a_json, data_catalog, reference_data):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 201
    draft = res.data

    res = admin_client.get(
        f"/v3/datasets/{draft['id']}/revisions", content_type="application/json"
    )
    assert res.status_code == 200
    assert isinstance(res.data, list)

    # FIXME:
    # Creating a dataset and each m2m change create a revision.
    # It would be better if revision was only created only
    # once, after all m2m changes have been done.
    assert len(res.data) == 1


def test_new_published_revisions(admin_client, dataset_a_json, data_catalog, reference_data):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.get(f"/v3/datasets/{dataset_id}/revisions", content_type="application/json")
    assert res.status_code == 200
    assert isinstance(res.data, list)
    assert len(res.data) == 1
    assert res.data[0]["published_revision"] == 1


def test_new_draft_publish_revisions(admin_client, dataset_a_json, data_catalog, reference_data):
    dataset_a_json["state"] = "draft"
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.post(f"/v3/datasets/{dataset_id}/publish", content_type="application/json")
    assert res.status_code == 200

    res = admin_client.get(f"/v3/datasets/{dataset_id}/revisions", content_type="application/json")
    assert res.status_code == 200
    assert isinstance(res.data, list)
    assert len(res.data) == 1
    assert res.data[0]["published_revision"] == 1


def test_merge_draft_revisions(admin_client, dataset_a_json, data_catalog, reference_data):
    res = admin_client.post("/v3/datasets", dataset_a_json, content_type="application/json")
    assert res.status_code == 201
    dataset_id = res.data["id"]

    res = admin_client.post(
        f"/v3/datasets/{dataset_id}/create-draft", dataset_a_json, content_type="application/json"
    )
    assert res.status_code == 201
    draft_id = res.data["id"]

    res = admin_client.post(f"/v3/datasets/{draft_id}/publish", content_type="application/json")
    assert res.status_code == 200

    res = admin_client.get(f"/v3/datasets/{dataset_id}/revisions", content_type="application/json")
    assert res.status_code == 200
    assert len(res.data) == 2
    assert res.data[0]["published_revision"] == 2
