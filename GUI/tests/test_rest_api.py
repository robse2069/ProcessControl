import json
import os
import time
from urllib import response
from urllib.request import urlopen

REST_API_URL = os.environ.get(
    "PROCESS_CONTROL_REST_URL",
    "http://127.0.0.1:8000/api/v1",
)
CSN_ID = 5


def get_json(path):
    with urlopen(REST_API_URL + path, timeout=2) as response:
        assert response.status == 200
        return json.load(response)


def test_rest_api_reads_configuration():
    response = get_json(f"/nodes/{CSN_ID}/configuration")

    assert response["can_id"] == CSN_ID
    assert response["name"] == "Ambient Temperature"
    assert response["unit"] == "°C"
    assert response["value_min"] == 0
    assert response["value_max"] == 100


def test_rest_api_reads_main_process_configuration():
    response = get_json("/configuration")

    assert response["communication_method"] == "simulated_node"
    assert response["gui_update_ms"] == 500
    assert response["logging_cycle_ms"] == 100


def test_rest_api_reads_ambient_temperature_value():
    response = get_json(f"/nodes/{CSN_ID}/values")

    assert response["node_id"] == CSN_ID
    assert 20 <= response["value"] <= 40

    time.sleep(20)
    assert response["node_id"] == CSN_ID
    assert 20 <= response["value"] <= 40
    