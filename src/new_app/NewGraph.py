"""

The different Graph widget for the different kind of graph we want

"""


from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from new_app.constants import CountRateReqParams, graph_line_style,axis_label_style,graph_title_style,GraphLineSetup
from new_app.constants import INTEGRATION_TIME,GRAPH_ANIMATION_INTERVAL
from new_app.NewService import get_accumulated_count, record_measurement_data
import pyqtgraph as pg

'''
Normal line Graph
'''
class RealTimeGraphsWidget(QWidget):


    def __init__(
            self,
            info_widget,
            param,
            repo,
            label_list,
            has_timer
        ):
            super().__init__()
            self.widget_info = info_widget
            self.param: CountRateReqParams = param
            self.label_list = label_list
            self.x_axis = []
            self.y_axis = [[]]*len(self.widget_info.lines)
            self.repo =repo
            self._init_graph()
            self.has_timer = has_timer # bool to activate the timer or not, if false is provided the graph will not refresh automaticly
            if self.has_timer:
                self._init_timer()

    def _init_graph(self):
        layout = QVBoxLayout(self)
        self.widget = pg.PlotWidget()
        self.widget.setTitle(self.widget_info.title, **graph_title_style)
        self.widget.setLabel("left", self.widget_info.vertical_axis_label, **axis_label_style)
        self.widget.setBackground(self.widget_info.background_color.value)
        self.widget.addLegend(offset=(10, 10))
        self.widget.showGrid(x=True, y=True)
        self._plot_lines(self.widget_info.lines)
        layout.addWidget(self.widget)
        self.setLayout(layout)

    #initialise the plot widget
    def _plot_lines(self, lines: list[GraphLineSetup]):
        self.widget._plotted_lines = [
            self.widget.plot(
                [0],
                [0],
                name=line.label,
                pen=pg.mkPen(color=line.color.value, **graph_line_style),
                symbol=line.symbol,
                symbolSize=5,
                symbolBrush=line.color.value,
            )
            for line in lines
        ]
    # if timer, init the timer with interval GRAPH_ANIMATION_INTERVAL found in constants.py
    def _init_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.timer.timeout.connect(self._update_plots)
        self.timer.start()

    #update the plots, either by the timer or by being called from eslewhere 
    def _update_plots(self,time=INTEGRATION_TIME):
        self.x_axis = self._update_x_axis_value(self.x_axis)
        if self.has_timer:
            new_data = record_measurement_data(self.param,self.repo,time)
        else :
            new_data = get_accumulated_count(self.param,self.repo,time)
        for index, graph_line in enumerate(self.widget._plotted_lines):
            self.y_axis[index] += new_data[index]
            graph_line.setData(self.x_axis, self.y_axis[index])
            label = self.label_list[index]
            label[0].setText(label[1]+f": {int(new_data[index])}")

    def _update_x_axis_value(self,x_axis_values) -> list[float]:
        previous_value = x_axis_values[-1] if x_axis_values else 0
        x_axis_values.append(previous_value + 1)
        # if len(x_axis_values) > 50:  
        #     x_axis_values.pop(0)
        return x_axis_values