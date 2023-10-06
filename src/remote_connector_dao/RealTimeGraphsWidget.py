from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph as pg
from remote_connector_dao.SignalCounter import SignalCounter
from remote_connector_dao.get_signal import get_count_rates
from remote_connector_dao.constants import GRAPH_ANIMATION_INTERVAL
from remote_connector_dao.app_styles import (
    colors,
    graph_line_style,
    axis_label_style,
    graph_title_style,
)


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

        self.single_counts_graph_widget = pg.PlotWidget()
        self.coincidences_graph_widget = pg.PlotWidget()
        self._set_graph_widget_style()
        self._set_single_counts_graph_lines()
        self._set_coincidences_graph_lines()

        self.update_graph_event()

        self._configure_layout()

    def _update_plot_data(self):
        self._update_counts()

        self.channel1_data_line.setData(
            self.signal_counter.elapsed_time, self.signal_counter.channel1
        )
        self.channel2_data_line.setData(
            self.signal_counter.elapsed_time, self.signal_counter.channel2
        )
        self.coincidences_data_line.setData(
            self.signal_counter.elapsed_time, self.signal_counter.coincidences
        )

    def _update_counts(self):
        channel1, channel2, coincidences = get_count_rates(
            self.timetagger_proxy, self.timetagger_controller, self.channels_list
        )

        self.signal_counter.record_measurement(channel1, channel2, coincidences)

    def _set_single_counts_graph_lines(self):
        channel1_line_pen = pg.mkPen(color=colors["red_primary"], **graph_line_style)
        self.channel1_data_line = self.single_counts_graph_widget.plot(
            self.signal_counter.elapsed_time,
            self.signal_counter.channel1,
            name="ch.1",
            pen=channel1_line_pen,
            symbol="s",
            symbolSize=5,
            symbolBrush=colors["red_primary"],
        )

        channel2_line_pen = pg.mkPen(color=colors["blue_primary"], **graph_line_style)

        self.channel2_data_line = self.single_counts_graph_widget.plot(
            self.signal_counter.elapsed_time,
            self.signal_counter.channel2,
            name="ch.2",
            pen=channel2_line_pen,
            symbol="o",
            symbolSize=5,
            symbolBrush=colors["blue_primary"],
        )

    def _set_coincidences_graph_lines(self):
        cc_12_line_pen = pg.mkPen(color=colors["red_primary"], **graph_line_style)
        self.coincidences_data_line = self.coincidences_graph_widget.plot(
            self.signal_counter.elapsed_time,
            self.signal_counter.coincidences,
            name="1-2",
            pen=cc_12_line_pen,
            symbol="s",
            symbolSize=5,
            symbolBrush=colors["red_primary"],
        )

    def update_graph_event(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.timer.timeout.connect(self._update_plot_data)
        self.timer.start()

    def _configure_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.single_counts_graph_widget)
        layout.addWidget(self.coincidences_graph_widget)
        self.setLayout(layout)

    def _set_graph_widget_style(self):
        self.single_counts_graph_widget.setBackground(colors["white_primary"])
        self.single_counts_graph_widget.setTitle("Single Counts", **graph_title_style)
        self.single_counts_graph_widget.setLabel(
            "left", "Counts / s", **axis_label_style
        )
        self.single_counts_graph_widget.addLegend(offset=(10, 10))
        self.single_counts_graph_widget.showGrid(x=True, y=True)
        self.single_counts_graph_widget.setMouseEnabled(x=False, y=True)

        self.coincidences_graph_widget.setBackground(colors["white_primary"])
        self.coincidences_graph_widget.setTitle("Coincidences", **graph_title_style)
        self.coincidences_graph_widget.setLabel("left", "CC/s", **axis_label_style)
        self.coincidences_graph_widget.addLegend(offset=(10, 10))
        self.coincidences_graph_widget.showGrid(x=True, y=True)
        self.coincidences_graph_widget.setMouseEnabled(x=False, y=True)
