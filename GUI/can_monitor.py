"""Print sensor values received from a SocketCAN interface.

The CAN interface and connected sensor nodes must already be configured before
starting this program.
"""

import argparse
from datetime import datetime

import can


DEFAULT_CHANNEL = "can0"
AMBIENT_TEMPERATURE_ID = 0x005
SENSOR_NAMES = {
    AMBIENT_TEMPERATURE_ID: "Ambient Temperature",
}


def decode_sensor_value(data):
    """Decode the sensor value from the first two bytes of a CAN payload."""
    if len(data) < 2:
        raise ValueError("sensor payload must contain at least two bytes")

    return int.from_bytes(data[0:2], byteorder="big", signed=True)


def format_message(message):
    """Format one received CAN message for terminal output."""
    name = SENSOR_NAMES.get(message.arbitration_id, "Unknown sensor")
    timestamp = datetime.fromtimestamp(message.timestamp).isoformat(
        timespec="milliseconds"
    )
    data = message.data.hex(" ")

    try:
        value = decode_sensor_value(message.data)
        value_text = f"value={value}"
    except ValueError as error:
        value_text = f"value=invalid ({error})"

    return (
        f"{timestamp} id=0x{message.arbitration_id:03X} "
        f"{name} {value_text} data={data}"
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Print values received from configured CAN sensor nodes."
    )
    parser.add_argument(
        "--channel",
        default=DEFAULT_CHANNEL,
        help=f"SocketCAN channel (default: {DEFAULT_CHANNEL})",
    )
    return parser.parse_args()


def monitor(channel):
    """Receive and print CAN messages until interrupted."""
    print(f"Listening on {channel}; press Ctrl+C to stop.")

    bus = can.Bus(interface="socketcan", channel=channel)
    try:
        while True:
            message = bus.recv(timeout=1.0)
            if message is not None:
                print(format_message(message), flush=True)
    finally:
        bus.shutdown()


def main():
    arguments = parse_arguments()
    try:
        monitor(arguments.channel)
    except KeyboardInterrupt:
        print("\nCAN monitor stopped.")
    except can.CanError as error:
        raise SystemExit(f"Unable to read {arguments.channel}: {error}") from error


if __name__ == "__main__":
    main()
