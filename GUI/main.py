"""Application entry point for the headless Process Control backend."""

import argparse
from pathlib import Path
import threading

from bus_communication import BusCommunication
from configuration import ConfigurationLoader
from rest_service import RestService
from scheduler import Logger, Scheduler


def create_application(config_file, host="127.0.0.1", port=8000,
             channel="can0"):
    configuration = ConfigurationLoader().load(config_file)
    bus = BusCommunication(configuration, channel=channel)
    logger = Logger(configuration)
    scheduler = Scheduler(configuration, bus, logger)
    rest_service = RestService(
        configuration,
        bus_communication=bus,
        logger=logger,
        host=host,
        port=port,
    )
    return configuration, bus, logger, scheduler, rest_service


def main():
    parser = argparse.ArgumentParser(description="Run the Process Control backend")
    parser.add_argument("--config", default="config.xml")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--channel", default="can0")
    arguments = parser.parse_args()

    configuration, bus, logger, scheduler, rest_service = create_application(
        Path(arguments.config), arguments.host, arguments.port, arguments.channel
    )
    rest_service.start()
    scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
    scheduler_thread.start()
    try:
        rest_service.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.stop()
        scheduler_thread.join(timeout=2)
        rest_service.shutdown()
        bus.close()


if __name__ == "__main__":
    main()
