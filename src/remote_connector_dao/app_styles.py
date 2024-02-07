from PyQt5 import QtCore
from enum import Enum


class Colors(Enum):
    WHITE_PRIMARY = "#FFFFFF"
    RED_PRIMARY = "#f81b0b"
    BLUE_PRIMARY = "#0a8def"
    GREEN_PRIMARY = "#2ef304"
    BLACK = "#000000"


graph_line_style = {"width": 3, "style": QtCore.Qt.SolidLine}

graph_title_style = {"color": Colors.BLACK.value, "size": "15pt"}

axis_label_style = {"font-size": "20pt", "color": Colors.BLACK.value}
