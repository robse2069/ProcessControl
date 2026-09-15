import json
import os
import csv
from pathlib import Path
import time
from urllib.request import Request, urlopen
import pytest

REST_API_URL = os.environ.get(
    "PROCESS_CONTROL_REST_URL",
    "http://127.0.0.1:8000/api/v1",
)
SIMULATED_REST_API_URL = os.environ.get(
    "PROCESS_CONTROL_SIMULATED_REST_URL",
    "http://127.0.0.1:8000/api/v1",
)
CSN_ID = 5


def get_json(path):
    with urlopen(REST_API_URL + path, timeout=2) as response:
        assert response.status == 200
        return json.load(response)


def post_json(path, payload, rest_url=REST_API_URL):
    request = Request(
        rest_url + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=2) as response:
        return response.status, json.load(response)


def stop_logging(rest_url=REST_API_URL):
    request = Request(rest_url + "/logging/stop", method="POST")
    with urlopen(request, timeout=2) as response:
        assert response.status == 200
        return json.load(response)


@pytest.mark.simulation_tests
def test_rest_api_reads_configuration():
    response = get_json(f"/nodes/{CSN_ID}/configuration")

    assert response["can_id"] == CSN_ID
    assert response["name"] == "Ambient Temperature"
    assert response["unit"] == "°C"
    assert response["value_min"] == 0
    assert response["value_max"] == 100


@pytest.mark.simulation_tests
def test_rest_api_reads_main_process_configuration():
    response = get_json("/configuration")

    assert response["communication_method"] == "simulated_node"
    assert response["gui_update_ms"] == 500
    assert response["logging_cycle_ms"] == 100

@pytest.mark.integration_tests
def test_rest_api_reads_main_process_configuration_real_can():
    response = get_json("/configuration")

    assert response["communication_method"] == "can"
    assert response["gui_update_ms"] == 500
    assert response["logging_cycle_ms"] == 100


@pytest.mark.integration_tests
def test_rest_api_reads_ambient_temperature_from_real_can():
    response = get_json(f"/nodes/{CSN_ID}/values")

    assert response["node_id"] == CSN_ID
    assert 20 <= response["value"] <= 40


@pytest.mark.simulation_tests
def test_rest_api_reads_ambient_temperature_value():
    response = get_json(f"/nodes/{CSN_ID}/values")

    assert response["node_id"] == CSN_ID
    assert 20 <= response["value"] <= 40


@pytest.mark.simulation_tests
def test_rest_api_logging_start_endpoint_exists():
    filename = "logging-start-endpoint.csv"
    created_file = None
    try:
        status, response = post_json(
            "/logging/start",
            {"filename": filename},
            SIMULATED_REST_API_URL,
        )
        assert status == 201
        created_file = Path(response["filename"])
        assert response["state"] == "active"
        assert response["filename"].endswith(".csv")
    finally:
        stop_logging(SIMULATED_REST_API_URL)
        if created_file is not None and created_file.exists():
            created_file.unlink()


@pytest.mark.simulation_tests
def test_rest_api_logging_creates_csv_file():
    filename = "logging-file-exists.csv"
    created_file = None
    try:
        status, response = post_json(
            "/logging/start",
            {"filename": filename},
            SIMULATED_REST_API_URL,
        )
        assert status == 201
        created_file = Path(response["filename"])
        time.sleep(5)
        stop_response = stop_logging(SIMULATED_REST_API_URL)

        assert stop_response["state"] == "inactive"
        assert created_file.suffix == ".csv"
        assert created_file.exists()
    finally:
        if created_file is not None and created_file.exists():
            created_file.unlink()


@pytest.mark.simulation_tests
@pytest.mark.parametrize(
    ("cycle_ms", "rest_url"),
    [
        (100, SIMULATED_REST_API_URL),
        (10, os.environ.get("PROCESS_CONTROL_SIMULATED_REST_URL_10MS")),
    ],
)
def test_rest_api_logging_csv_content(cycle_ms, rest_url):
    if rest_url is None:
        pytest.skip("PROCESS_CONTROL_SIMULATED_REST_URL_10MS is not configured")

    runtime_seconds = 5
    sensor_interval_ms = 500
    filename = f"logging-content-{cycle_ms}ms.csv"
    created_file = None
    try:
        request = Request(
            rest_url + "/logging/start",
            data=json.dumps({"filename": filename}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2) as response:
            assert response.status == 201
            start_response = json.load(response)

        created_file = Path(start_response["filename"])
        time.sleep(runtime_seconds)

        stop_request = Request(rest_url + "/logging/stop", method="POST")
        with urlopen(stop_request, timeout=2) as response:
            assert response.status == 200

        with created_file.open(newline="", encoding="utf-8") as logfile:
            rows = list(csv.DictReader(logfile))

        expected_entries = (runtime_seconds * 1000) // sensor_interval_ms
        minimum_entries = int(expected_entries * 0.8)
        maximum_entries = int(expected_entries * 1.2) + 1

        assert minimum_entries <= len(rows) <= maximum_entries
        assert rows
        assert set(rows[0]) == {
            "timestamp_utc",
            "timestamp_unix_ns",
            "sequence",
            "can_id",
            "sensor_name",
            "value",
            "unit",
            "data_hex",
        }
        assert [int(row["sequence"]) for row in rows] == list(
            range(1, len(rows) + 1)
        )
        assert all(row["timestamp_utc"].endswith("Z") for row in rows)
        timestamps = [int(row["timestamp_unix_ns"]) for row in rows]
        assert timestamps == sorted(timestamps)
        assert all(row["can_id"] == str(CSN_ID) for row in rows)
        assert all(row["sensor_name"] == "Ambient Temperature" for row in rows)
        assert all(row["unit"] == "°C" for row in rows)
        assert all(20 <= int(row["value"]) <= 40 for row in rows)
        assert all(row["data_hex"] == "001e00000000026d" for row in rows)

        intervals = [
            current - previous
            for previous, current in zip(timestamps, timestamps[1:])
        ]
        expected_interval_ns = sensor_interval_ms * 1_000_000
        expected_minimum = expected_interval_ns * 0.8
        expected_maximum = expected_interval_ns * 1.3
        intervals_in_range = [
            interval
            for interval in intervals
            if expected_minimum <= interval <= expected_maximum
        ]
        assert len(intervals_in_range) >= len(intervals) * 0.8
        assert expected_minimum <= sum(intervals) / len(intervals) <= expected_maximum
    finally:
        if created_file is not None and created_file.exists():
            created_file.unlink()


@pytest.mark.integration_tests
def test_rest_api_logging_csv_content_real_can():
    runtime_seconds = 5
    cycle_ms = 100
    filename = "logging-content-real-can.csv"
    created_file = None
    try:
        status, response = post_json(
            "/logging/start",
            {"filename": filename},
            REST_API_URL,
        )
        assert status == 201
        created_file = Path(response["filename"])

        time.sleep(runtime_seconds)
        stop_response = stop_logging(REST_API_URL)
        assert stop_response["state"] == "inactive"

        with created_file.open(newline="", encoding="utf-8") as logfile:
            rows = list(csv.DictReader(logfile))

        expected_entries = (runtime_seconds * 1000) // cycle_ms
        minimum_entries = int(expected_entries * 0.8)
        maximum_entries = int(expected_entries * 1.2) + 1

        assert minimum_entries <= len(rows) <= maximum_entries
        assert rows
        assert set(rows[0]) == {
            "timestamp_utc",
            "timestamp_unix_ns",
            "sequence",
            "can_id",
            "sensor_name",
            "value",
            "unit",
            "data_hex",
        }
        assert [int(row["sequence"]) for row in rows] == list(
            range(1, len(rows) + 1)
        )
        assert all(row["timestamp_utc"].endswith("Z") for row in rows)
        timestamps = [int(row["timestamp_unix_ns"]) for row in rows]
        assert timestamps == sorted(timestamps)
        assert all(row["can_id"] == str(CSN_ID) for row in rows)
        assert all(row["sensor_name"] == "Ambient Temperature" for row in rows)
        assert all(row["unit"] == "°C" for row in rows)
        assert all(20 <= int(row["value"]) <= 40 for row in rows)
        assert all(len(row["data_hex"]) == 16 for row in rows)
        assert all(
            bytes.fromhex(row["data_hex"])
            for row in rows
        )

        intervals = [
            current - previous
            for previous, current in zip(timestamps, timestamps[1:])
        ]
        expected_interval_ns = cycle_ms * 1_000_000
        expected_minimum = expected_interval_ns * 0.8
        expected_maximum = expected_interval_ns * 1.2
        intervals_in_range = [
            interval
            for interval in intervals
            if expected_minimum <= interval <= expected_maximum
        ]
        assert len(intervals_in_range) >= len(intervals) * 0.8
        assert expected_minimum <= sum(intervals) / len(intervals) <= expected_maximum
    finally:
        pass
        # if created_file is not None and created_file.exists():
        #     created_file.unlink()
