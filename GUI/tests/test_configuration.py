from pathlib import Path

import pytest

from configuration import ConfigurationLoader


CONFIGURATION_FILE = Path(__file__).parents[1] / "config.xml"


@pytest.fixture
def configuration():
    return ConfigurationLoader().load(CONFIGURATION_FILE)


def test_loads_configured_controls(configuration):
    controls = {control.name: control for control in configuration.controls}

    assert set(controls) == {
        "GOx pre",
        "GOx Main",
        "Ethanol pre",
        "Ethanol Main",
    }
    assert controls["GOx pre"].can_id == 1
    assert controls["Ethanol Main"].can_id == 162


def test_loads_configured_measurements(configuration):
    measurements = {
        measurement.name: measurement
        for measurement in configuration.measurements
    }

    assert set(measurements) == {"Voltage", "Ambient Temperature"}
    assert measurements["Voltage"].can_id == 42
    assert measurements["Voltage"].unit == "Volt"


def test_loads_ambient_temperature_configuration(configuration):
    ambient_temperature = next(
        measurement
        for measurement in configuration.measurements
        if measurement.can_id == 5
    )

    assert ambient_temperature.name == "Ambient Temperature"
    assert ambient_temperature.minimum == 0
    assert ambient_temperature.maximum == 100
    assert ambient_temperature.unit == "°C"


def test_loads_communication_and_timing_configuration(configuration):
    assert configuration.communication_method == "simulated_node"
    assert configuration.gui_update_ms == 500
    assert configuration.logging_cycle_ms == 100
