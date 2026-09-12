"""Timestamped CSV logging for sensor messages."""

import csv
from datetime import datetime, timezone
import threading
from pathlib import Path
import time


class Logger:
    def __init__(self, configuration):
        self.configuration = configuration
        self.active = False
        self.filename = None
        self.records_written = 0
        self._sequence = 0
        self._last_message = None
        self._file = None
        self._writer = None
        self._lock = threading.Lock()
        self._wall_clock_ns = time.time_ns()
        self._monotonic_ns = time.perf_counter_ns()

    def start(self, filename):
        requested = Path(filename)
        if requested.name != filename or requested.suffix.lower() != ".csv":
            raise ValueError("filename must be a safe .csv filename")

        with self._lock:
            if self.active:
                raise RuntimeError("logging is already active")
            self._file = requested.open("w", newline="", encoding="utf-8")
            self._writer = csv.DictWriter(
                self._file,
                fieldnames=[
                    "timestamp_utc",
                    "timestamp_unix_ns",
                    "sequence",
                    "can_id",
                    "sensor_name",
                    "value",
                    "unit",
                    "data_hex",
                ],
            )
            self._writer.writeheader()
            self._file.flush()
            self.filename = str(requested.resolve())
            self.records_written = 0
            self._sequence = 0
            self.active = True

    def stop(self):
        with self._lock:
            self.active = False
            if self._file is not None:
                self._file.close()
            self._file = None
            self._writer = None

    def record(self, message):
        with self._lock:
            if message is not None:
                self._last_message = message
            if not self.active or self._last_message is None:
                return

            message = self._last_message
            measurement = next(
                (
                    item
                    for item in self.configuration.measurements
                    if item.can_id == message.arbitration_id
                ),
                None,
            )
            if measurement is None:
                return

            value = int.from_bytes(
                message.data[:2],
                byteorder="big",
                signed=True,
            )
            timestamp_unix_ns = (
                self._wall_clock_ns
                + time.perf_counter_ns()
                - self._monotonic_ns
            )
            now = datetime.fromtimestamp(
                timestamp_unix_ns / 1_000_000_000,
                timezone.utc,
            )
            self._sequence += 1
            self._writer.writerow({
                "timestamp_utc": now.isoformat(timespec="microseconds").replace(
                    "+00:00", "Z"
                ),
                "timestamp_unix_ns": timestamp_unix_ns,
                "sequence": self._sequence,
                "can_id": message.arbitration_id,
                "sensor_name": measurement.name,
                "value": value,
                "unit": measurement.unit,
                "data_hex": message.data.hex(),
            })
            self._file.flush()
            self.records_written += 1
