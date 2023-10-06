from PyQt5.QtWidgets import QMainWindow
from remote_connector_dao.RealTimeGraphsWidget import RealTimeGraphsWidget
from remote_connector_dao.SignalCounter import SignalCounter


class MainWindow(QMainWindow):
    def __init__(
        self, timetagger_proxy, timetagger_controller, channels, *args, **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.signal_counter = SignalCounter()
        self.channels_list = channels
        self.timetagger_proxy = timetagger_proxy
        self.timetagger_controller = timetagger_controller

        self.widget = RealTimeGraphsWidget(
            self.signal_counter,
            self.timetagger_proxy,
            self.timetagger_controller,
            self.channels_list,
        )
        self.setCentralWidget(self.widget)
