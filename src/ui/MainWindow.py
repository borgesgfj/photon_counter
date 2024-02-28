from PyQt5.QtWidgets import QMainWindow
from AppController import AppController
from ui.graphs.RealTimeGraphsWidget import RealTimeGraphsWidget
from time_tagger.measurement.service import MeasurementService, CountRateReqParams
from ui.graphs.GraphWidget2D import WidgetInfo, GraphLineSetup
from ui.styles import Color
from time_tagger.measurement.repository import MeasurementType
from AppController import AppController

from ui.styles import Color
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
        self.coincidence_v = coincidence_virtual_channels
        self.timetagger_proxy = timetagger_proxy
        self.device_serial_number = device_serial_number
        self.measurement_service = measurement_service
        self._init_graph_widget()

    def _init_graph_widget(self):
        # Test for the new RealTimeGraphWidget it will be remove
        line_setup = [
            GraphLineSetup(
                label="ch.1",
                symbol="s",
                color=Color.RED_PRIMARY,
                initial_data=[[[0.0], [0]]],
            )
        ]
       
        
        coincidence_count_params =CountRateReqParams([1,2],
                                                       self.device_serial_number,
                                                       self.timetagger_proxy,
                                                       MeasurementType.HISTOGRAM)
    
        coincidence_widget_info_ = WidgetInfo("Coincidence",line_setup,
                                 "1-2",Color.WHITE_PRIMARY,True)
        widget = (coincidence_widget_info_, coincidence_count_params)
        self.graph_widge = RealTimeGraphsWidget([widget],measaurement_service= self.measurement_service)
        self.setCentralWidget(self.graph_widge) 
        
        