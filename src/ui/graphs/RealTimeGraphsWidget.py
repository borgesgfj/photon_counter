from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from shared.constants.constants import GRAPH_ANIMATION_INTERVAL
import time_tagger
from ui.styles import Color
from ui.graphs.GraphWidget2D import GraphWidget2D, GraphLineSetup
from AppController import AppController, CountRateReqParams
from time_tagger.measurement.service import MeasurementService


class RealTimeGraphsWidget(QWidget):
    def __init__(
        self,
        info_widget,
        param,
        measaurement_service,
    ):
        super().__init__()

        self.widget_info = info_widget
        self.measurement_service = measaurement_service
        self.param: CountRateReqParams = param
        self.timer_delay = 1
        self.x_axis = []
        self._init_graph()
        self._update_graph_event()

    def _init_graph(self):
        layout = QVBoxLayout(self)

        if self.widget_info.is_histogram:
            self.timer_delay = 4
        self.widget = GraphWidget2D(self.widget_info)
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def _update_plots(self):
         #maybe not needed anymore because of the refactoring of the main windows
        if self.widget_info.is_histogram:
            data = self.measurement_service.getData_histo(self.param)
            self.widget.update_lines_data(data[0],[data[1]])
        else:
            self.x_axis = self._update_x_axis_value(self.x_axis)
            new_data = self.measurement_service.record_measurement_data(self.param)
            self.widget.update_lines_data(self.x_axis,new_data)

    def _update_graph_event(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL*self.timer_delay)
        self.timer.timeout.connect(self._update_plots)
        self.timer.start()

    def _update_x_axis_value(self,x_axis_values) -> list[float]:
        previous_value = x_axis_values[-1] if x_axis_values else 0
        x_axis_values.append(previous_value + 1)
        # if len(x_axis_values) > 50:
        #     x_axis_values.pop(0)
        return x_axis_values

class MeasureGraphsWidget(QWidget):
    def __init__(
        self,
        info_widget,
        param,
        measaurement_service
    ):
        super().__init__()

        self.widget_info = info_widget
        self.measurement_service = measaurement_service
        self.param = param
        self.timer_delay = 1
        self._init_graph()

    def _init_graph(self):
        layout = QVBoxLayout(self)
        self.x_axis = []
        self.y_data = []
        for line in self.widget_info.lines:
            self.y_data += [[]]
        self.widget = GraphWidget2D(self.widget_info)
        #self.widget = [self.widget_info[1],graph_widget,x_axis]#maybe not needed anymore because of the refactoring of the main windows
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def update_plot(self,time):
        self._update_x_axis_value()
        new_data = self.measurement_service.get_accumulated_count(self.param,time)
        self.widget.update_lines_data(self.x_axis,new_data)
        return new_data[:,-1]

    def _update_x_axis_value(self):
        previous_value = self.x_axis[-1] if self.x_axis else 0
        self.x_axis.append(previous_value + 1)
        # if len(self.x_axis) > 50:
        #     self.x_axis.pop(0)
