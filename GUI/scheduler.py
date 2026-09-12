"""Periodic coordination of bus updates and logging."""

import threading
import time


class Scheduler:
    def __init__(self, configuration, bus_communication, logger=None):
        self.configuration = configuration
        self.bus_communication = bus_communication
        self.logger = logger
        self.cycle_time = min(
            configuration.gui_update_ms,
            configuration.logging_cycle_ms,
        ) / 1000.0
        self.stop_event = threading.Event()

    def run_once(self):
        messages = self.bus_communication.poll_all()
        if self.logger is not None:
            for message in messages:
                self.logger.record(message)
        return messages

    def run(self):
        next_run = time.monotonic()
        while not self.stop_event.is_set():
            self.run_once()
            next_run += self.cycle_time
            remaining = next_run - time.monotonic()
            if remaining <= 0:
                next_run = time.monotonic()
                continue
            if self.cycle_time >= 0.02:
                self.stop_event.wait(remaining)
                continue
            while remaining > 0 and not self.stop_event.is_set():
                time.sleep(0)
                remaining = next_run - time.monotonic()

    def stop(self):
        self.stop_event.set()
