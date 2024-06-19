from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from shared.constants.constants import GRAPH_ANIMATION_INTERVAL
from ui.styles import Color
from ui.graphs.GraphWidget2D import GraphWidget2D, GraphLineSetup
from AppController import AppController, CountRateReqParams
from time_tagger.measurement.service import MeasurementService


class RealTimeGraphsWidget(QWidget):
    def __init__(
        self,
        info_widget_list,
        measaurement_service
    ):
        super().__init__()

        self.widget_info_list = info_widget_list #maybe not needed anymore because of the refactoring of the main windows
        self.measurement_service = measaurement_service
        self.widget_list = []
        self.timer_delay = 1
        self._init_graph()
        self._update_graph_event()

    def _init_graph(self):
        layout = QVBoxLayout(self)
        for widget_info in self.widget_info_list:
            if widget_info[0].is_histogram:
                self.timer_delay = 4
            graph_widget = GraphWidget2D(widget_info[0])
            x_axis = [] # each plot get a x-axis, maybe not needed ?
            self.widget_list += [[widget_info[1],graph_widget,x_axis]] #maybe not needed anymore because of the refactoring of the main windows
            layout.addWidget(graph_widget)
        self.setLayout(layout)

    def _update_plots(self):
        for widget in self.widget_list: #maybe not needed anymore because of the refactoring of the main windows
            if widget[1].is_histogram:
                data = self.measurement_service.getData_histo(widget[0])
                widget[1].update_lines_data(data[0],[data[1]])
            else:
                widget[2]= self. _update_x_axis_value(widget[2])
                new_data = self.measurement_service.record_measurement_data(widget[0])
                widget[1].update_lines_data(widget[2],new_data)

    def _update_graph_event(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL*self.timer_delay)
        self.timer.timeout.connect(self._update_plots)
        self.timer.start()

    def _update_x_axis_value(self,x_axis_values) -> list[float]:
        previous_value = x_axis_values[-1] if x_axis_values else 0
        x_axis_values.append(previous_value + 1)
        if len(x_axis_values) > 50:
            x_axis_values.pop(0)
        return x_axis_values
