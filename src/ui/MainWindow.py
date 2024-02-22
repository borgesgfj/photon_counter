from PyQt5.QtWidgets import QMainWindow
from AppController import AppController
from ui.graphs.RealTimeGraphsWidget import RealTimeGraphsWidget
from time_tagger.measurement.service import MeasurementService


class MainWindow(QMainWindow):
    def __init__(
        self,
        timetagger_proxy,
        device_serial_number,
        channels,
        coincidence_virtual_channels,
        app_controller: AppController,
        measurement_service: MeasurementService,
        *args,
        **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.app_controller = app_controller
        self.channels_list = channels
        self.timetagger_proxy = timetagger_proxy
        self.device_serial_number = device_serial_number

        self.widget = RealTimeGraphsWidget(
            app_controller=self.app_controller,
            time_tagger_proxy=self.timetagger_proxy,
            channels=self.channels_list,
            device_serial=self.device_serial_number,
            coincidence_virtual_channels=coincidence_virtual_channels,
            measurement_service=measurement_service,
        )
        self.setCentralWidget(self.widget)
