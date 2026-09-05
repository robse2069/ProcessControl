"""Communication handlers for simulated and SocketCAN nodes."""

from dataclasses import dataclass
import time

try:
    import can
except ImportError:
    can = None


@dataclass
class BusMessage:
    arbitration_id: int
    data: bytes
    timestamp: float


def decode_sensor_value(data):
    if len(data) < 2:
        raise ValueError("sensor payload must contain at least two bytes")
    return int.from_bytes(data[:2], byteorder="big", signed=True)


class SimulatedNode:
    """Produce the fixed CSN frame every half second."""

    def __init__(self, interval=0.5):
        self.interval = interval
        self.next_send = time.monotonic()

    def receive(self):
        now = time.monotonic()
        if now < self.next_send:
            return None
        self.next_send = now + self.interval
        return BusMessage(
            arbitration_id=5,
            data=bytes.fromhex("00 1e 00 00 00 00 02 6d"),
            timestamp=time.time(),
        )

    def close(self):
        return None


class RealCanBus:
    def __init__(self, channel="can0"):
        if can is None:
            raise RuntimeError("python-can is required for real CAN communication")
        self.bus = can.Bus(interface="socketcan", channel=channel)

    def receive(self):
        message = self.bus.recv(timeout=0)
        if message is None:
            return None
        return BusMessage(
            arbitration_id=message.arbitration_id,
            data=bytes(message.data),
            timestamp=message.timestamp,
        )

    def close(self):
        self.bus.shutdown()


class BusCommunication:
    def __init__(self, configuration, channel="can0"):
        self.configuration = configuration
        if configuration.communication_method == "simulated_node":
            self.handler = SimulatedNode()
        else:
            self.handler = RealCanBus(channel)

    def poll(self):
        message = self.handler.receive()
        if message is None:
            return None

        for measurement in self.configuration.measurements:
            if measurement.can_id == message.arbitration_id:
                measurement.value = decode_sensor_value(message.data)
        return message

    def close(self):
        self.handler.close()
