from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from shared.constants.constants import GRAPH_ANIMATION_INTERVAL
from ui.styles import Color
from ui.graphs.GraphWidget2D import GraphWidget2D, GraphLineSetup
from AppController import AppController, CountRateReqParams
from time_tagger.measurement.repository import MeasurementType
from time_tagger.measurement.service import MeasurementService


class RealTimeGraphsWidget(QWidget):
    def __init__(
        self,
        app_controller: AppController,
        measurement_service: MeasurementService,
        time_tagger_proxy,
        channels: list[int],
        device_serial: str,
        coincidence_virtual_channels: list[int],
    ):
        super().__init__()
        self.channels_list = channels
        self.device_serial = device_serial
        self.time_tagger_proxy = time_tagger_proxy
        self.app_controller = app_controller
        self.measurement_service = measurement_service
        self.coincidence_virtual_channels = coincidence_virtual_channels
        self.x_axis_values = []

        single_counts_lines = [
            GraphLineSetup(
                label="ch.1",
                symbol="s",
                color=Color.RED_PRIMARY,
                initial_data=[[[0.0], [0]]],
            ),
            GraphLineSetup(
                label="ch.2",
                symbol="o",
                color=Color.BLUE_PRIMARY,
                initial_data=[[[0.0], [0]]],
            ),
        ]
        self.single_counts_graph = GraphWidget2D(
            lines=single_counts_lines,
            vertical_axis_label="Counts / s",
            graph_title="Single Counts",
        )

        self.coincidences_graph = GraphWidget2D(
            lines=[
                GraphLineSetup(
                    label="1-2",
                    symbol="s",
                    color=Color.RED_PRIMARY,
                    initial_data=[[[0.0], [0]]],
                ),
            ],
            vertical_axis_label="Coincidences / s",
            graph_title="Coincidences",
        )

        self._update_graph_event()

        self._configure_layout()

    def _update_plots(self):
        single_count_data = self.measurement_service.record_measurement_data(
            CountRateReqParams(
                channels=self.channels_list,
                device_serial=self.device_serial,
                time_tagger_network_proxy=self.time_tagger_proxy,
                measurement_type=MeasurementType.SINGLE_COUNTS,
            )
        )

        coincidences_data = self.measurement_service.record_measurement_data(
            CountRateReqParams(
                channels=self.coincidence_virtual_channels,
                device_serial=self.device_serial,
                time_tagger_network_proxy=self.time_tagger_proxy,
                measurement_type=MeasurementType.COINCIDENCES,
            )
        )

        x_axis = self._update_x_axis_value()

        self.single_counts_graph.update_lines_data(
            new_x_data=x_axis, new_lines_y_data=single_count_data
        )
        self.coincidences_graph.update_lines_data(
            new_x_data=x_axis, new_lines_y_data=coincidences_data
        )

    def _update_x_axis_value(self) -> list[float]:
        previous_value = self.x_axis_values[-1] if self.x_axis_values else 0

        self.x_axis_values.append(previous_value + 1)

        if len(self.x_axis_values) > 50:
            self.x_axis_values.pop(0)

        return self.x_axis_values

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
