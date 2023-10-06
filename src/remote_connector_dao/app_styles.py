from PyQt5 import QtCore

colors = {
    "white_primary": "#FFFFFF",
    "red_primary": "#f81b0b",
    "blue_primary": "#0a8def",
    "green_primary": "#2ef304",
    "black": "#000000",
}

graph_line_style = {"width": 3, "style": QtCore.Qt.SolidLine}

graph_title_style = {
    "color": colors["black"],
    "size": "15pt"
}

axis_label_style = {
    "font-size": "10pt",
    "color": colors["black"]
}
