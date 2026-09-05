"""Load and validate the Process Control XML configuration."""

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass
class ControlConfiguration:
    name: str
    set_value: int
    value: int
    minimum: int
    maximum: int
    unit: str
    can_id: int
    type: str


@dataclass
class MeasurementConfiguration:
    name: str
    value: int
    minimum: int
    maximum: int
    unit: str
    can_id: int


@dataclass
class Configuration:
    controls: list
    measurements: list
    communication_method: str
    gui_update_ms: int
    logging_cycle_ms: int


class ConfigurationLoader:
    def load(self, filename):
        root = ET.parse(Path(filename)).getroot()

        controls = [
            ControlConfiguration(
                name=element.attrib["name"],
                set_value=int(element.attrib["setValue"]),
                value=int(element.attrib["value"]),
                minimum=int(element.attrib["minValue"]),
                maximum=int(element.attrib["maxValue"]),
                unit=element.attrib["unit"],
                can_id=int(element.attrib["MsgID"]),
                type=element.attrib["type"],
            )
            for element in root.findall("control")
        ]
        measurements = [
            MeasurementConfiguration(
                name=element.attrib["name"],
                value=int(element.attrib["value"]),
                minimum=int(element.attrib["minValue"]),
                maximum=int(element.attrib["maxValue"]),
                unit=element.attrib["unit"],
                can_id=int(element.attrib["MsgID"]),
            )
            for element in root.findall("measurement")
        ]

        communication = root.find("communication")
        gui_update = root.findtext("GUIUpdate")
        logging = root.find("logging[@name='cycletime']")
        if communication is None or gui_update is None or logging is None:
            raise ValueError("config.xml is missing required runtime settings")

        return Configuration(
            controls=controls,
            measurements=measurements,
            communication_method=communication.attrib["method"],
            gui_update_ms=int(gui_update.strip()),
            logging_cycle_ms=int(logging.attrib["value"]),
        )
