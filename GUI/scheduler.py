"""Periodic coordination of bus updates and logging."""

import threading
import time


class Scheduler:
    def __init__(self, configuration, bus_communication, logger=None):
        self.configuration = configuration
        self.bus_communication = bus_communication
        self.logger = logger
        self.cycle_time = configuration.gui_update_ms / 1000.0
        self.stop_event = threading.Event()

    def run_once(self):
        message = self.bus_communication.poll()
        if message is not None and self.logger is not None:
            self.logger.record(message)
        return message

    def run(self):
        while not self.stop_event.is_set():
            started = time.monotonic()
            self.run_once()
            remaining = self.cycle_time - (time.monotonic() - started)
            if remaining > 0:
                self.stop_event.wait(remaining)

    def stop(self):
        self.stop_event.set()


class Logger:
    def __init__(self, configuration):
        self.configuration = configuration
        self.active = False
        self.filename = None
        self.records = []

    def start(self, filename):
        self.filename = filename
        self.active = True

    def stop(self):
        self.active = False

    def record(self, message):
        if self.active:
            self.records.append(message)
