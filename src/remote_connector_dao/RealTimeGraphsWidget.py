from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph as pg
from remote_connector_dao.SignalCounter import SignalCounter
from remote_connector_dao.get_signal import get_count_rates
from remote_connector_dao.constants import GRAPH_ANIMATION_INTERVAL


class RealTimeGraphsWidget(QWidget):
    def __init__(
        self,
        timetagger_proxy,
        timetagger_controller,
        channels,
    ):
        super().__init__()
        self.signal_counter = SignalCounter()
        self.channels_list = channels
        self.timetagger_proxy = timetagger_proxy
        self.timetagger_controller = timetagger_controller

        self.single_counts_graph_widget = pg.PlotWidget()
        self.coincidences_graph_widget = pg.PlotWidget()

        self.elapsed_time = self.signal_counter.elapsed_time
        self.channel1_counts = self.signal_counter.channel1
        self.channel2_counts = self.signal_counter.channel2
        self.coincidences = self.signal_counter.coincidences

        self._set_single_counts_graph_lines()
        self._set_coincidences_graph_lines()

        self._set_update_graph_event()

        self._configure_layout()

    def _update_plot_data(self):
        self._update_counts()

        self.channel1_data_line.setData(self.elapsed_time, self.channel1_counts)
        self.channel2_data_line.setData(self.elapsed_time, self.channel2_counts)
        self.coincidences_data_line.setData(self.elapsed_time, self.coincidences)

    def _update_counts(self):
        channel1, channel2, coincidences = get_count_rates(
            self.timetagger_proxy, self.timetagger_controller, self.channels_list
        )

        self.signal_counter.record_measurement(channel1, channel2, coincidences)

    def _set_single_counts_graph_lines(self):
        self.channel1_data_line = self.single_counts_graph_widget.plot(
            self.elapsed_time, self.channel1_counts
        )

        self.channel2_data_line = self.single_counts_graph_widget.plot(
            self.elapsed_time, self.channel2_counts
        )

    def _set_coincidences_graph_lines(self):
        self.coincidences_data_line = self.coincidences_graph_widget.plot(
            self.elapsed_time, self.coincidences
        )

    def _set_update_graph_event(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.timer.timeout.connect(self._update_plot_data)
        self.timer.start()

    def _configure_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.single_counts_graph_widget)
        layout.addWidget(self.coincidences_graph_widget)
        self.setLayout(layout)
