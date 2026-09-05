"""HTTP REST interface for the Process Control backend."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import re


class RestService:
    def __init__(self, configuration, bus_communication=None, logger=None,
             host="127.0.0.1", port=8000):
        self.configuration = configuration
        self.bus_communication = bus_communication
        self.logger = logger
        self.host = host
        self.port = port
        self.server = None

    def get_configuration(self):
        return {
            "communication_method": self.configuration.communication_method,
            "gui_update_ms": self.configuration.gui_update_ms,
            "logging_cycle_ms": self.configuration.logging_cycle_ms,
        }

    def _measurement(self, can_id):
        for measurement in self.configuration.measurements:
            if measurement.can_id == can_id:
                return measurement
        raise KeyError(can_id)

    def get_node_configuration(self, can_id):
        measurement = self._measurement(can_id)
        return {
            "name": measurement.name,
            "unit": measurement.unit,
            "value": measurement.value,
            "value_set": 0,
            "value_default": 0,
            "value_min": measurement.minimum,
            "value_max": measurement.maximum,
            "value_offset": 0,
            "value_multiplier": 1000,
            "update_rate_ms": self.configuration.gui_update_ms,
            "node_type": 0,
            "can_id": measurement.can_id,
            "last_error_code": 0,
        }

    def get_node_values(self, can_id):
        measurement = self._measurement(can_id)
        return {
            "node_id": measurement.can_id,
            "value": measurement.value,
            "min_value": measurement.minimum,
            "max_value": measurement.maximum,
            "set_value": 0,
            "default_value": 0,
            "state": "running",
            "error_code": 0,
        }

    def start(self):
        service = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format_string, *args):
                return

            def send_json(self, status, payload):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                try:
                    if self.path == "/api/v1/configuration":
                        self.send_json(200, service.get_configuration())
                        return

                    match = re.fullmatch(
                        "/api/v1/nodes/(\\d+)/configuration", self.path
                    )
                    if match:
                        self.send_json(200, service.get_node_configuration(int(match.group(1))))
                        return

                    match = re.fullmatch("/api/v1/nodes/(\\d+)/values", self.path)
                    if match:
                        self.send_json(200, service.get_node_values(int(match.group(1))))
                        return

                    if self.path == "/api/v1/logging/status":
                        self.send_json(200, service.logging_status())
                        return

                    self.send_json(404, {"error": "resource not found"})
                except KeyError:
                    self.send_json(404, {"error": "node not found"})

            def do_POST(self):
                if self.path == "/api/v1/logging/stop":
                    if service.logger is not None:
                        service.logger.stop()
                    self.send_json(200, service.logging_status())
                    return
                self.send_json(404, {"error": "resource not found"})

        self.server = ThreadingHTTPServer((self.host, self.port), Handler)
        self.port = self.server.server_port
        return self.server

    def serve_forever(self):
        if self.server is None:
            self.start()
        self.server.serve_forever()

    def shutdown(self):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def logging_status(self):
        if self.logger is None:
            return {"state": "inactive", "filename": None, "records_written": 0}
        return {
            "state": "active" if self.logger.active else "inactive",
            "filename": self.logger.filename,
            "records_written": len(self.logger.records),
        }
