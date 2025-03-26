from dataclasses import dataclass
from enum import Enum


"""
    File that hold the enums and constants need for the new app

"""


class Color(Enum):
    WHITE_PRIMARY = "#FFFFFF"
    RED_PRIMARY = "#f81b0b"
    BLUE_PRIMARY = "#0a8def"
    GREEN_PRIMARY = "#2ef304"
    BLACK = "#000000"

Color_List = [Color.BLUE_PRIMARY,Color.GREEN_PRIMARY,Color.RED_PRIMARY,Color.BLACK]