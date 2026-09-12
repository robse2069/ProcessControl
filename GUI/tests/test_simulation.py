import csv
from dataclasses import replace

import pytest

from bus_communication import BusCommunication
from configuration import ConfigurationLoader
from logger import Logger
from scheduler import Scheduler


CONFIGURATION_FILE = "config.xml"


@pytest.mark.simulation_tests
def test_multiple_sensor_messages_between_logging_cycles_are_preserved(
    tmp_path,
    monkeypatch,
):
    configuration = ConfigurationLoader().load(CONFIGURATION_FILE)
    configuration = replace(
        configuration,
        communication_method="simulated_multisensor",
        gui_update_ms=100,
        logging_cycle_ms=100,
    )
    bus = BusCommunication(configuration)
    logger = Logger(configuration)
    scheduler = Scheduler(configuration, bus, logger)
    filename = "multiple-sensors.csv"
    monkeypatch.chdir(tmp_path)

    try:
        logger.start(str(filename))
        first_cycle_messages = scheduler.run_once()
        second_cycle_messages = scheduler.run_once()
        logger.stop()

        assert [message.arbitration_id for message in first_cycle_messages] == [
            5,
            6,
            5,
        ]
        assert second_cycle_messages == []

        with (tmp_path / filename).open(
            newline="",
            encoding="utf-8",
        ) as logfile:
            rows = list(csv.DictReader(logfile))

        assert [row["can_id"] for row in rows] == ["5", "6", "5"]
        assert [row["sensor_name"] for row in rows] == [
            "Ambient Temperature",
            "Ambient Pressure",
            "Ambient Temperature",
        ]
        assert [row["value"] for row in rows] == ["30", "1013", "31"]
        assert [row["unit"] for row in rows] == ["°C", "hPa", "°C"]
    finally:
        bus.close()
        if (tmp_path / filename).exists():
            (tmp_path / filename).unlink()
