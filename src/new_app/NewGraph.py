"""

The different Graph widget for the different kind of graph we want

"""


from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from new_app.constants import CountRateReqParams, graph_line_style,axis_label_style,graph_title_style,GraphLineSetup
from new_app.constants import INTEGRATION_TIME,GRAPH_ANIMATION_INTERVAL
from new_app.NewService import get_accumulated_count, record_measurement_data, histo_service
import pyqtgraph as pg
import numpy as np

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
            self.y_axis = []
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
            if len(self.y_axis) <= index :
                self.y_axis += [[new_data[index]]]
            else :
                self.y_axis[index] += [new_data[index]]
            graph_line.setData(self.x_axis, self.y_axis[index])
            label = self.label_list[index]
            label[0].setText(label[1]+f": {int(new_data[index])}")

    def _update_x_axis_value(self,x_axis_values) -> list[float]:
        previous_value = x_axis_values[-1] if x_axis_values else 0
        x_axis_values.append(previous_value + 1)
        # if len(x_axis_values) > 50:  
        #     x_axis_values.pop(0)
        return x_axis_values
    

"""
Histogram graph
"""
class ThreadHistoWidget(QWidget):
    def __init__(
        self,
        info_widget,
        param,
        repo,
        label,
        min_histo,
        max_histo,
    ):
        super().__init__()
        self.widget_info = info_widget
        self.param: CountRateReqParams = param
        self._init_graph()
        # self._init_timer()
        self.label = label
        self.repo = repo
        self.min_histo = min_histo
        self.max_histo = max_histo
        self.init_thread()
        self._init_timer()

    def _init_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.timer.timeout.connect(self.start_thread)
        self.timer.start()

    def start_thread(self):
        # if not self.thread.isRunning():
        self.thread.start()

    def init_thread(self):
        self.thread = QtCore.QThread()
        self.worker = histo_service(self.param)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.getData_histo)
        self.worker.data.connect(self._update_plots)
        # self.thread.start()

    def _init_graph(self):
        layout = QVBoxLayout(self)
        self.widget = pg.PlotWidget()
        self.widget.plotItem.setMouseEnabled(x=True,y=False)
        self.widget.setTitle(self.widget_info.title, **graph_title_style)
        self.widget.setLabel("left", self.widget_info.vertical_axis_label, **axis_label_style)
        self.widget.setBackground(self.widget_info.background_color.value)
        self.widget.addLegend(offset=(10, 10))
        self.widget.showGrid(x=True, y=True)
        self._plot_lines(self.widget_info.lines)
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def _plot_lines(self, line: GraphLineSetup):
        self.widget._plotted_lines = self.widget.plot(
                [0],
                [0],
                name=line.label,
                pen=pg.mkPen(color=line.color.value, width= 0.9),
                symbol=line.symbol,
                symbolSize=5,
                symbolBrush=line.color.value,
                fillLevel = 0,
                fillBrush=line.color.value,
                stepMode= "right",
            )

    def _update_plots(self,data):
        # data = service.getData_histo(self.param,self.repo)
        y_data = data[1]
        x_axis = data[0]
        key = (self.param.histogram_measurement,self.param.measurement_type)
        self.repo.save_data(key,data)
        if self.min_histo != None:
            filter_min = x_axis>=self.min_histo
            x_axis = x_axis[filter_min]
            y_data = y_data[filter_min]

        if self.max_histo != None:
            filter_max = x_axis<=self.max_histo
            x_axis = x_axis[filter_max]
            y_data = y_data[filter_max]

        label =self.label
        label[0].setText(label[1]+f": Max: {np.max(y_data)},time: {x_axis[np.argmax(y_data)]}")
        self.widget._plotted_lines.setData(x_axis, y_data)
        self.thread.exit()

        self.thread.wait()