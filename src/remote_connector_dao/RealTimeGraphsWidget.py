from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from remote_connector_dao.SignalCounter import SignalCounter
from remote_connector_dao.get_signal import get_count_rates
from remote_connector_dao.constants import GRAPH_ANIMATION_INTERVAL
from remote_connector_dao.GraphWidget2D import GraphWidget2D


class RealTimeGraphsWidget(QWidget):
    def __init__(
        self,
        signal_counter: SignalCounter,
        timetagger_proxy,
        timetagger_controller,
        channels,
    ):
        super().__init__()
        self.signal_counter = signal_counter
        self.channels_list = channels
        self.timetagger_proxy = timetagger_proxy
        self.timetagger_controller = timetagger_controller

        self.single_counts_graph = GraphWidget2D(
            number_of_lines=2,
            graph_lines_data=[
                [signal_counter.elapsed_time, signal_counter.channel1],
                [signal_counter.elapsed_time, signal_counter.channel2],
            ],
            vertical_axis_label="Counts / s",
            graph_title="Single Counts",
            graph_line_labels_list=["ch.1", "ch.2"],
        )

        self.coincidences_graph = GraphWidget2D(
            number_of_lines=1,
            graph_lines_data=[
                [signal_counter.elapsed_time, signal_counter.coincidences]
            ],
            vertical_axis_label="Coincidences / s",
            graph_title="Coincidences",
            graph_line_labels_list=["1-2"],
        )

        self._update_graph_event()

        self._configure_layout()

    def _update_plots(self):
        self._update_counts()
        new_single_counts_data = [
            [self.signal_counter.elapsed_time, self.signal_counter.channel1],
            [self.signal_counter.elapsed_time, self.signal_counter.channel2],
        ]

        new_coincidence_count_data = [
            [self.signal_counter.elapsed_time, self.signal_counter.coincidences]
        ]

        self.single_counts_graph.update_lines_data(new_single_counts_data)
        self.coincidences_graph.update_lines_data(new_coincidence_count_data)

    def _update_counts(self):
        channel1, channel2, coincidences = get_count_rates(
            self.timetagger_proxy, self.timetagger_controller, self.channels_list
        )

        self.signal_counter.record_measurement(channel1, channel2, coincidences)

    def _update_graph_event(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.timer.timeout.connect(self._update_plots)
        self.timer.start()

    def _configure_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.single_counts_graph)
        layout.addWidget(self.coincidences_graph)
        self.setLayout(layout)
