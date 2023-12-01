"""Test the API."""

import uuid

import pytest
import requests

from e_commerce_ddd import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_allocations_are_persisted(add_stock):
    sku = random_sku()
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)
    add_stock(
        [
            (batch1, sku, 10, "2011-01-01"),
            (batch2, sku, 10, "2011-01-02"),
        ]
    )
    line_1 = {"orderid": order1, "sku": sku, "qty": 10}
    line_2 = {"orderid": order2, "sku": sku, "qty": 10}
    url = config.get_api_url()

    # First order uses up all stock in batch 1
    response = requests.post(f"{url}/allocate", json=line_1)
    assert response.status_code == 201
    assert response.json()["batchref"] == batch1

    # Second order should go to batch2
    response = requests.post(f"{url}/allocate", json=line_2)
    assert response.status_code == 201
    assert response.json()["batchref"] == batch2


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, other_sku = random_sku(), random_sku("other")
    early_batch = random_batchref(1)
    later_batch = random_batchref(2)
    other_batch = random_batchref(3)
    add_stock(
        [
            (later_batch, sku, 100, "2011-01-02"),
            (early_batch, sku, 100, "2011-01-01"),
            (other_batch, other_sku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    response = requests.post(f"{url}/allocate", json=data)

    assert response.status_code == 201
    assert response.json()["batchref"] == early_batch


@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_orderid()
    data = {"orderid": order_id, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()

    response = requests.post(f"{url}/allocate", json=data)

    assert response.status_code == 400
    assert response.json()["message"] == f"Invalid sku {unknown_sku}"
