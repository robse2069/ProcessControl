"""Robot Framework library and mock server for the Process Control REST API v1."""

import json
import re
import threading
from datetime import datetime, timezone
from enum import IntEnum
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen


NODE_ID = 2047


class NodeType(IntEnum):
    """Descriptive names for the numeric CSN node type values."""

    SENSOR_RESISTIVE = 0
    SENSOR_RESISTIVE_DIFFERENTIAL = 1
    SENSOR_VOLTAGE = 2
    SENSOR_VOLTAGE_DIFFERENTIAL = 3
    SENSOR_FREQUENCY = 4
    SENSOR_PULSEWIDTH = 5
    ACTOR_ON_OFF = 10
    ACTOR_PWM = 11
    ACTOR_MOTOR = 12


class _MockBackend:
    def __init__(self):
        self.logging_state = "inactive"
        self.logging_filename = None
        self.records_written = 0
        self.failure_status = None
        self.configuration = {
            "name": "CSN test node",
            "unit": "Volt",
            "value": 120,
            "value_set": 100,
            "value_default": 0,
            "value_min": -100,
            "value_max": 500,
            "value_offset": 0,
            "value_multiplier": 1000,
            "update_rate_ms": 500,
            "node_type": NodeType.SENSOR_VOLTAGE,
            "can_id": NODE_ID,
            "last_error_code": 0,
        }

    @staticmethod
    def timestamp():
        return datetime.now(timezone.utc).isoformat()

    def health(self):
        status = self.failure_status
        if status == 503:
            health_status = "unavailable"
        elif status:
            health_status = "degraded"
        else:
            health_status = "ok"
        return {
            "status": health_status,
            "timestamp": self.timestamp(),
            "software": {
                "gui": "2.0.0",
                "backend": "2.0.0",
                "configurator": "2.0.0",
            },
            "backend": {
                "rest_api": "v1",
                "can": {"status": "connected", "interface": "can0"},
            },
            "connected_csn": [{
                "node_id": NODE_ID,
                "firmware_version": "1.3.0",
                "hardware_version": "1.0",
                "status": "connected",
                "last_seen": self.timestamp(),
            }],
            "recent_errors": [],
        }

    def runtime_values(self, node_id):
        if node_id != NODE_ID:
            raise ApiError(404, "NODE_NOT_FOUND", "Requested node is unknown")
        return {
            "node_id": node_id,
            "value": self.configuration["value"],
            "min_value": self.configuration["value_min"],
            "max_value": self.configuration["value_max"],
            "set_value": self.configuration["value_set"],
            "default_value": self.configuration["value_default"],
            "state": "running",
            "error_code": self.configuration["last_error_code"],
            "timestamp": self.timestamp(),
        }

    def validate_node(self, node_id):
        if node_id != NODE_ID:
            raise ApiError(404, "NODE_NOT_FOUND", "Requested node is unknown")


class ApiError(Exception):
    def __init__(self, status, code, message, details=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}


class _Handler(BaseHTTPRequestHandler):
    backend = None

    def log_message(self, format_string, *args):
        return

    def _send(self, status, payload):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _error(self, error):
        self._send(error.status, {
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
            },
            "timestamp": self.backend.timestamp(),
        })

    def _json(self):
        length = int(self.headers.get("Content-Length", "0"))
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, TypeError):
            raise ApiError(400, "INVALID_JSON", "Request body is not valid JSON")

    def _dispatch(self):
        if self.command == "GET" and self.path == "/api/v1/health":
            return 200, self.backend.health()

        if self.backend.failure_status:
            status = self.backend.failure_status
            code = {409: "REQUEST_BUSY", 500: "BACKEND_ERROR", 503: "CAN_UNAVAILABLE", 504: "CAN_TIMEOUT"}.get(
                status, "REQUEST_FAILED"
            )
            raise ApiError(status, code, "Injected mock failure")

        match = re.fullmatch(r"/api/v1/nodes/(\d+)/values", self.path)
        if self.command == "GET" and match:
            return 200, self.backend.runtime_values(int(match.group(1)))

        match = re.fullmatch(r"/api/v1/nodes/(\d+)/configuration", self.path)
        if self.command == "GET" and match:
            self.backend.validate_node(int(match.group(1)))
            return 200, self.backend.configuration
        if self.command == "PUT" and match:
            self.backend.validate_node(int(match.group(1)))
            data = self._json()
            required = {
                "name", "unit", "value", "value_set", "value_default", "value_min",
                "value_max", "value_offset", "value_multiplier", "update_rate_ms",
                "node_type", "can_id", "last_error_code",
            }
            if set(data) != required:
                raise ApiError(422, "INVALID_CONFIGURATION", "Complete configuration is required")
            self.backend.configuration = data
            return 200, {"accepted": True, "configuration": data}

        match = re.fullmatch(r"/api/v1/nodes/(\d+)/setup", self.path)
        if self.command == "POST" and match:
            self.backend.validate_node(int(match.group(1)))
            return 200, {"node_id": int(match.group(1)), "configuration": self.backend.configuration}

        match = re.fullmatch(r"/api/v1/nodes/(\d+)/setup/complete", self.path)
        if self.command == "POST" and match:
            self.backend.validate_node(int(match.group(1)))
            return 200, {"node_id": int(match.group(1)), "accepted": True}

        if self.command == "POST" and self.path == "/api/v1/logging/start":
            data = self._json()
            filename = data.get("filename")
            if not isinstance(filename, str) or not filename or "/" in filename or "\\" in filename:
                raise ApiError(400, "INVALID_FILENAME", "filename must be a safe file name")
            self.backend.logging_filename = filename
            self.backend.logging_state = "active"
            self.backend.records_written = 0
            return 201, {"state": "active", "filename": filename}

        if self.command == "POST" and self.path == "/api/v1/logging/stop":
            self.backend.logging_state = "inactive"
            return 200, {"state": "inactive", "filename": self.backend.logging_filename}

        if self.command == "GET" and self.path == "/api/v1/logging/status":
            return 200, {"state": self.backend.logging_state,
                         "filename": self.backend.logging_filename,
                         "started_at": None,
                         "records_written": self.backend.records_written}

        raise ApiError(404, "RESOURCE_NOT_FOUND", "Requested resource is unknown")

    def _handle(self):
        try:
            status, payload = self._dispatch()
            self._send(status, payload)
        except ApiError as error:
            self._error(error)
        except Exception as error:
            self._error(ApiError(500, "BACKEND_ERROR", str(error)))

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle


class MockRestApiLibrary:
    """Robot Framework keywords for testing the REST interface against a mock Backend."""

    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self.server = None
        self.thread = None
        self.base_url = None
        self.last_status = None
        self.last_json = None
        self.backend = None

    def start_mock_backend(self):
        self.backend = _MockBackend()
        _Handler.backend = self.backend
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.base_url = "http://127.0.0.1:{}/api/v1".format(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop_mock_backend(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.thread = None

    def set_mock_failure_status(self, status):
        self.backend.failure_status = int(status)

    def clear_mock_failure(self):
        self.backend.failure_status = None

    def request(self, method, path, body=None):
        payload = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(self.base_url + path, data=payload, method=method,
                          headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=2) as response:
                self.last_status = response.status
                self.last_json = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            self.last_status = error.code
            self.last_json = json.loads(error.read().decode("utf-8"))

    def request_health(self):
        self.request("GET", "/health")

    def request_node_values(self, node_id):
        self.request("GET", "/nodes/{}/values".format(node_id))

    def request_node_setup(self, node_id):
        self.request("POST", "/nodes/{}/setup".format(node_id))

    def request_configuration(self, node_id):
        self.request("GET", "/nodes/{}/configuration".format(node_id))

    def write_configuration(self, node_id, configuration):
        self.request("PUT", "/nodes/{}/configuration".format(node_id), configuration)

    def complete_node_setup(self, node_id):
        self.request("POST", "/nodes/{}/setup/complete".format(node_id))

    def start_logging(self, filename):
        self.request("POST", "/logging/start", {"filename": filename})

    def stop_logging(self):
        self.request("POST", "/logging/stop")

    def request_logging_status(self):
        self.request("GET", "/logging/status")

    def response_status_should_be(self, expected):
        if self.last_status != int(expected):
            raise AssertionError("Expected HTTP {}, got {}: {}".format(expected, self.last_status, self.last_json))

    def response_field_should_be(self, field, expected):
        actual = self.last_json
        for part in field.split("."):
            actual = actual[part]
        if actual != expected:
            raise AssertionError("Expected {}={}, got {}".format(field, expected, actual))

    def response_field_should_exist(self, field):
        actual = self.last_json
        for part in field.split("."):
            if not isinstance(actual, dict) or part not in actual:
                raise AssertionError("Missing response field {}".format(field))
            actual = actual[part]

    def response_recent_errors_should_not_exceed(self, limit):
        errors = self.last_json["recent_errors"]
        if len(errors) > int(limit):
            raise AssertionError("Expected no more than {} errors, got {}".format(limit, len(errors)))
