from dataclasses import dataclass

import pyqtgraph as pg
from ui.styles import Color, axis_label_style, graph_line_style, graph_title_style
import numpy as np

@dataclass
class GraphLineSetup:
    label: str
    symbol: str
    color: Color
    # TODO: can be further improved by using namedtuple
    initial_data: tuple[float, float]


"""
Struct to pass the data to init the graph widget

"""
@dataclass
class WidgetInfo:
    title : str
    lines : list[GraphLineSetup]
    vertical_axis_label : str
    background_color:Color
    is_histogram : bool = False 




class GraphWidget2D(pg.PlotWidget):
    def __init__(
        self,
        widget_info: WidgetInfo
    ):
        super().__init__()
        self.setTitle(widget_info.title, **graph_title_style)
        self.setLabel("left", widget_info.vertical_axis_label, **axis_label_style)
        self._set_graph_basic_configurations(widget_info.background_color)
        self.is_histogram = widget_info.is_histogram
        self._plotted_lines = self._plot_lines(widget_info.lines)
    
    def _plot_lines(self, lines: list[GraphLineSetup]):
        # Test to plot the data as an histogram
        if self.is_histogram:
            return [
                self.plot(
                    line.initial_data[0][0],
                    line.initial_data[0][1],
                    name=line.label,
                    pen=pg.mkPen(color=line.color.value, width= 0.9),
                    symbol=line.symbol,
                    symbolSize=5,
                    symbolBrush=line.color.value,
                    fillLevel = 0,
                    fillBrush=line.color.value,
                    stepMode= "right",
                )
                for line in lines
            ]
        
        else:
            return [
                self.plot(
                    line.initial_data[0][0],
                    line.initial_data[0][1],
                    name=line.label,
                    pen=pg.mkPen(color=line.color.value, **graph_line_style),
                    symbol=line.symbol,
                    symbolSize=5,
                    symbolBrush=line.color.value,
                )
                for line in lines
            ]

    def _set_graph_basic_configurations(self, background_color: Color):
        self.setBackground(background_color.value)
        self.addLegend(offset=(10, 10))
        self.showGrid(x=True, y=True)
        self.setMouseEnabled(x=False, y=True)

    def update_lines_data(
        self, new_x_data: list[int], new_lines_y_data: list[list[float]]
    ):
        if self.is_histogram :
            for index, graph_line in enumerate(self._plotted_lines): 
                new_y_data = new_lines_y_data[index]
                graph_line.setData(new_x_data,new_y_data)
        else:
            for index, graph_line in enumerate(self._plotted_lines):
                new_y_data = new_lines_y_data[index]
                graph_line.setData(new_x_data, new_y_data)
