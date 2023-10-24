import datetime
import logging

import pytest

from apps.core.models import DatasetPublisher

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.dataset]


def test_create_publisher(admin_client, publisher_a_json):
    res = admin_client.post("/v3/publishers", publisher_a_json, content_type="application/json")
    logger.info(f"{res.data=}")
    assert res.status_code == 201


def test_create_publisher_twice(admin_client, publisher_b_json):
    _now = datetime.datetime.now()
    res1 = admin_client.post("/v3/publishers", publisher_b_json, content_type="application/json")
    assert res1.status_code == 201
    logger.info(f"{res1.data=}")
    res2 = admin_client.post("/v3/publishers", publisher_b_json, content_type="application/json")
    assert res2.status_code == 201
    assert res1.data.get("id") != res2.data.get("id")


def test_create_publisher_error(admin_client, publisher_error_json):
    response = admin_client.post(
        "/v3/publishers", publisher_error_json, content_type="application/json"
    )
    assert response.status_code == 400


def test_list_publishers(client, post_publisher_payloads_a_b_c_d):
    response = client.get("/v3/publishers")
    logger.info(f"{response.data=}")
    publisher_count = DatasetPublisher.available_objects.all().count()
    assert response.status_code == 200
    assert len(response.data.get("results")) == publisher_count


@pytest.mark.parametrize(
    "publisher_filter, filter_value, filter_result",
    [
        ("name", "sija C", 1),
        ("homepage__url", "yyy", 2),
        ("homepage__title", "website", 5),
        ("homepage__title", "C kotisivu", 1),
    ],
)
def test_list_publishers_with_filter(
    client,
    post_publisher_payloads_a_b_c_d,
    publisher_filter,
    filter_value,
    filter_result,
):
    url = "/v3/publishers?{0}={1}".format(publisher_filter, filter_value)
    logger.info(url)
    response = client.get(url)
    logger.info(f"{response.data=}")
    assert response.status_code == 200
    assert len(response.data.get("results")) == filter_result


def test_list_publishers_with_offset_pagination(client, post_publisher_payloads_a_b_c_d):
    url = "/v3/publishers?{0}={1}".format("limit", 2)
    logger.info(url)
    response = client.get(url)
    logger.info(f"{response.data=}")
    assert response.status_code == 200
    assert response.data.get("next") is not None


def test_change_publisher(admin_client, publisher_c_json, publisher_put_c_json):
    _now = datetime.datetime.now()
    res1 = admin_client.post("/v3/publishers", publisher_c_json, content_type="application/json")
    publisher_created = DatasetPublisher.objects.get(id=res1.data.get("id"))
    assert publisher_created.name["en"] == "Publisher C"
    response = admin_client.put(
        "/v3/publishers/{id}".format(id=res1.data.get("id")),
        publisher_put_c_json,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert res1.data.get("id") == response.data.get("id")
    logger.info(str(response.data))
    publisher_changed = DatasetPublisher.objects.get(id=res1.data.get("id"))
    assert publisher_changed.name["en"] == "Publisher C with new page"
    homepages = publisher_changed.homepage.all()
    assert homepages[0].url == "http://uusi.c.publisher.xyz/"
    assert homepages[0].title["en"] == "Publisher new C website"


def test_get_publisher_by_id(admin_client, post_publisher_payloads_a_b_c_d):
    response = admin_client.get("/v3/publishers")
    results = response.data.get("results")
    for result in results:
        publisher_by_id = admin_client.get("/v3/publishers/{id}".format(id=result.get("id")))
        assert response.status_code == 200
        assert publisher_by_id.data.get("name") == result.get("name")


def test_delete_publisher_by_id(admin_client, post_publisher_payloads_a_b_c_d):
    response = admin_client.get("/v3/publishers")
    publisher_count = DatasetPublisher.available_objects.all().count()
    assert response.data.get("count") == publisher_count
    results = response.data.get("results")
    delete_result = admin_client.delete("/v3/publishers/{id}".format(id=results[0].get("id")))
    assert delete_result.status_code == 204
    assert publisher_count - 1 == DatasetPublisher.available_objects.all().count()


@pytest.mark.parametrize(
    "publisher_order, order_result",
    [
        ("created", "Publisher A"),
        ("-created", "Publisher D"),
        ("url,created", "Publisher D"),
        ("-url,created", "Publisher C"),
    ],
)
def test_list_publishers_with_ordering(
    client, post_publisher_payloads_a_b_c_d, publisher_order, order_result
):
    url = "/v3/publishers?ordering={0}".format(publisher_order)
    res = client.get(url)
    assert res.status_code == 200
    results = res.data.get("results")
    assert results[0].get("name").get("en") == order_result
