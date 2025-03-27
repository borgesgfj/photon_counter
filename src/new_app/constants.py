from dataclasses import dataclass
from enum import Enum
from PyQt5 import QtCore

"""
    File that hold the enums and constants need for the new app

"""
INTEGRATION_TIME = 0.5e12  # IN PICOSECONDS
TRIGGER_VOLTAGE = 0.12  # VALUE IN VOLTS
SLEEP_TIME = 10e-12
GRAPH_ANIMATION_INTERVAL = int(INTEGRATION_TIME * (1e-9))  # IN MILLISECONDS
#-------- ENU----------
class Widget_Layout(Enum):
    SINGLE_COIN = "Single and Coincidence"
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

Color_List = [Color.BLUE_PRIMARY,Color.GREEN_PRIMARY,Color.RED_PRIMARY,Color.BLACK]

graph_line_style = {"width": 3, "style": QtCore.Qt.SolidLine}

graph_title_style = {"color": Color.BLACK.value, "size": "15pt"}

axis_label_style = {"font-size": "20pt", "color": Color.BLACK.value}



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