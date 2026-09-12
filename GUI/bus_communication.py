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

    def receive_all(self):
        message = self.receive()
        return [] if message is None else [message]

    def close(self):
        return None


class SimulatedMultiSensorNode(SimulatedNode):
    """Produce temperature and pressure frames in one bus interval."""

    def receive_all(self):
        now = time.monotonic()
        if now < self.next_send:
            return []
        self.next_send = now + self.interval
        timestamp = time.time()
        return [
            BusMessage(
                arbitration_id=5,
                data=bytes.fromhex("00 1e 00 00 00 00 02 6d"),
                timestamp=timestamp,
            ),
            BusMessage(
                arbitration_id=6,
                data=bytes.fromhex("03 f5 00 00 00 00 02 6d"),
                timestamp=timestamp,
            ),
            BusMessage(
                arbitration_id=5,
                data=bytes.fromhex("00 1f 00 00 00 00 02 6d"),
                timestamp=timestamp,
            ),
        ]


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

    def receive_all(self):
        messages = []
        while True:
            message = self.receive()
            if message is None:
                return messages
            messages.append(message)

    def close(self):
        self.bus.shutdown()


class BusCommunication:
    def __init__(self, configuration, channel="can0"):
        self.configuration = configuration
        if configuration.communication_method == "simulated_node":
            self.handler = SimulatedNode()
        elif configuration.communication_method == "simulated_multisensor":
            self.handler = SimulatedMultiSensorNode()
        else:
            self.handler = RealCanBus(channel)

    def poll(self):
        messages = self.poll_all()
        return messages[0] if messages else None

    def poll_all(self):
        messages = self.handler.receive_all()
        for message in messages:
            for measurement in self.configuration.measurements:
                if measurement.can_id == message.arbitration_id:
                    measurement.value = decode_sensor_value(message.data)
        return messages

    def close(self):
        self.handler.close()
