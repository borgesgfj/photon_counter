import pyqtgraph as pg

from remote_connector_dao.app_styles import (
    Colors,
    graph_line_style,
    axis_label_style,
    graph_title_style,
)

LINE_COLORS = [color.value for color in Colors if color.value != "#FFFFFF"]

LINE_SYMBOLS = ["s", "o", "t", "+"]


class GraphWidget2D(pg.PlotWidget):
    def __init__(
        self,
        number_of_lines,
        graph_lines_data,
        graph_title,
        vertical_axis_label,
        graph_line_labels_list,
        background_color=Colors.WHITE_PRIMARY.value,
    ):
        super().__init__()
        self.graph_lines = []
        self.graph_lines_data = graph_lines_data
        self.number_of_lines = number_of_lines
        self.graph_line_labels_list = graph_line_labels_list
        self.background_color = background_color

        self.setTitle(graph_title, **graph_title_style)
        self.setLabel("left", vertical_axis_label, **axis_label_style)
        self._set_graph_basic_configurations()

        self._create_graph_lines()

    def _create_graph_lines(self):
        for i in range(self.number_of_lines):
            line_color = LINE_COLORS[i]
            x_data = self.graph_lines_data[i][0]
            y_data = self.graph_lines_data[i][1]

            line_pen = pg.mkPen(color=line_color, **graph_line_style)

            line = self.plot(
                x_data,
                y_data,
                name=self.graph_line_labels_list[i],
                pen=line_pen,
                symbol=LINE_SYMBOLS[i],
                symbolSize=5,
                symbolBrush=line_color,
            )
            self.graph_lines.append(line)

    def _set_graph_basic_configurations(self):
        self.setBackground(self.background_color)
        self.addLegend(offset=(10, 10))
        self.showGrid(x=True, y=True)
        self.setMouseEnabled(x=False, y=True)

    def update_lines_data(self, new_lines_data):
        for index, graph_line in enumerate(self.graph_lines):
            new_x_data = new_lines_data[index][0]
            new_y_data = new_lines_data[index][1]

            graph_line.setData(new_x_data, new_y_data)
