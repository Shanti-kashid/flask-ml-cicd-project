import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Iris Species Predictor" in r.data


def test_valid_prediction(client):
    r = client.post("/api/predict", json={
        "sepal_length": 5.1, "sepal_width": 3.5,
        "petal_length": 1.4, "petal_width": 0.2})
    assert r.status_code == 200
    assert r.get_json()["species"] == "setosa"


def test_invalid_input_returns_400(client):
    r = client.post("/api/predict", json={"sepal_length": "abc"})
    assert r.status_code == 400


def test_metrics_endpoint(client):
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"app_requests_total" in r.data
