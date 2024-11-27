from dataclasses import dataclass
from enum import Enum


#-------- ENU----------
class Widget_Layout(Enum):
    SINGLE_COIN = "Single and Coincidence"
    SINGLE_COUNT = "Single count"
    COIN_COUNT = "Coincidence rate"
    MEASUREMENT ="Measurement"
    HISTOGRAM = "Coincidence histogram"

class MeasurementType(Enum):
    SINGLE_COUNTS = "SINGLE_COUNTS"
    COINCIDENCES = "COINCIDENCES"
    HISTOGRAM = "HISTOGRAM"
    HISTOGRAM_CORR = "HISTOGRAM_CORR"

class Color(Enum):
    WHITE_PRIMARY = "#FFFFFF"
    RED_PRIMARY = "#f81b0b"
    BLUE_PRIMARY = "#0a8def"
    GREEN_PRIMARY = "#2ef304"
    BLACK = "#000000"


@dataclass
class GraphLineSetup:
    label: str
    symbol: str
    color: Color

@dataclass
class WidgetInfo:
    title : str
    lines : list[GraphLineSetup]|GraphLineSetup
    vertical_axis_label : str
    background_color:Color
    is_histogram : bool = False

@dataclass
class Constant:
    INTEGRATION_TIME = 0.5e12  # IN PICOSECONDS
    TRIGGER_VOLTAGE = 0.12  # VALUE IN VOLTS
    SLEEP_TIME = 10e-12
    GRAPH_ANIMATION_INTERVAL = int(INTEGRATION_TIME * (1e-9))

@dataclass
class CountRateReqParams:
    channels: list[int]
    device_serial: str
    time_tagger: object
    measurement_type: MeasurementType
    histogram_measurement= None
    bin_width = 50
    n_bin = 200
