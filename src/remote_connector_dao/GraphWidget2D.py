from dataclasses import dataclass

import pyqtgraph as pg

from remote_connector_dao.app_styles import (
    Colors,
    graph_line_style,
    axis_label_style,
    graph_title_style,
)


@dataclass
class GraphLineSetup:
    label: str
    symbol: str
    color: Colors

    # TODO: can be further improved by using namedtuple
    initial_data: tuple[float, float]


class GraphWidget2D(pg.PlotWidget):
    def __init__(
        self,
        lines: list[GraphLineSetup],
        graph_title,
        vertical_axis_label,
        background_color=Colors.WHITE_PRIMARY,
    ):
        super().__init__()
        self.setTitle(graph_title, **graph_title_style)
        self.setLabel("left", vertical_axis_label, **axis_label_style)
        self._set_graph_basic_configurations(background_color)

        self._plotted_lines = self._plot_lines(lines)

    def _plot_lines(self, lines: list[GraphLineSetup]):
        return [
            self.plot(
                line.initial_data[0],
                line.initial_data[1],
                name=line.label,
                pen=pg.mkPen(color=line.color, **graph_line_style),
                symbol=line.symbol,
                symbolSize=5,
                symbolBrush=line.color,
            )
            for line in lines
        ]

    def _set_graph_basic_configurations(self, background_color: Colors):
        self.setBackground(background_color.value)
        self.addLegend(offset=(10, 10))
        self.showGrid(x=True, y=True)
        self.setMouseEnabled(x=False, y=True)

    def update_lines_data(self, new_lines_data):
        for index, graph_line in enumerate(self._plotted_lines):
            new_x_data = new_lines_data[index][0]
            new_y_data = new_lines_data[index][1]

            graph_line.setData(new_x_data, new_y_data)
