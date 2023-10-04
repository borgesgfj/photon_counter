from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMainWindow
import pyqtgraph as pg
from remote_connector_dao.SignalCounter import SignalCounter
from remote_connector_dao.get_signal import get_count_rates
from remote_connector_dao.constants import GRAPH_ANIMATION_INTERVAL
import sys


class MainWindow(QMainWindow):
    def __init__(
        self,
        signal_counter: SignalCounter,
        timetagger_proxy,
        timetagger_controller,
        channels,
        *args,
        **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.channels_list = channels
        self.timetagger_proxy = timetagger_proxy
        self.timetagger_controller = timetagger_controller

        self.signal_counter = signal_counter
        self.single_counts_graph_widget = pg.PlotWidget()
        self.coincidences_graph_widget = pg.PlotWidget()

        self.elapsed_time = signal_counter.elapsed_time
        self.channel1_counts = signal_counter.channel1
        self.channel2_counts = signal_counter.channel2
        self.coincidences = signal_counter.coincidences

        self.channel1_data_line = self.single_counts_graph_widget.plot(
            self.elapsed_time, self.channel1_counts
        )
        self.channel2_data_line = self.single_counts_graph_widget.plot(
            self.elapsed_time, self.channel2_counts
        )

        self.coincidences_data_line = self.coincidences_graph_widget.plot(
            self.elapsed_time, self.coincidences
        )
        layout = QVBoxLayout()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        layout.addWidget(self.single_counts_graph_widget)
        layout.addWidget(self.coincidences_graph_widget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_plot_data(self):
        channel1_counts, channel2_counts, coincidences_counts = get_count_rates(
            self.timetagger_proxy, self.timetagger_controller, self.channels_list
        )

        self.signal_counter.record_measurement(
            channel1_counts, channel2_counts, coincidences_counts
        )

        self.channel1_data_line.setData(self.elapsed_time, self.channel1_counts)
        self.channel2_data_line.setData(self.elapsed_time, self.channel2_counts)
        self.coincidences_data_line.setData(self.elapsed_time, self.coincidences)
