from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget,  QComboBox, QCheckBox, QGroupBox
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
        #self._init_graph_widget()
        self._init_interface()

    def _init_interface(self):
        self.v_left_layout  = QVBoxLayout()
        v_right_layout = QVBoxLayout()
        
        items = ["Single count","Correlation rate","Correlation histogram"]
        self.selector = QComboBox()
        self.selector.addItems(items)
        self.selector.activated.connect(self._show_graph)
        v_right_layout.addWidget(self.selector)

        self.main_button_list = []
        box = QGroupBox("Main Channel")
        box_layout = QVBoxLayout()
        for channel in range(4): 
            
            check = QCheckBox(f"ch {channel+1}")
            if channel == 0: check.setChecked(True)
            check.stateChanged.connect(self._show_graph)
            self.main_button_list += [check]
            box_layout.addWidget(check)
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)

        self.check_button_list = []
        box = QGroupBox("Second Channel")
        box_layout = QVBoxLayout()
        for channel in range(4): 
            check = QCheckBox(f"ch {channel+1}")
            if channel == 1: check.setChecked(True)
            check.stateChanged.connect(self._show_graph)
            self.check_button_list += [check]
            box_layout.addWidget(check)
             
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)


        self._show_graph()
        hlayout = QHBoxLayout()
        self._init_graph_widget((1,2))
        hlayout.addLayout(self.v_left_layout)
        hlayout.addLayout(v_right_layout)
        
        widget = QWidget()
        widget.resize(800,600)
        widget.setLayout(hlayout)
        self.setCentralWidget(widget) 



    def _show_graph(self):
        graph_type = self.selector.currentText()
        match graph_type:
            case "Single count":
                for i,m_channel in enumerate(self.main_button_list):
                    if m_channel.isChecked():
                        for j,s_channel in enumerate(self.check_button_list):
                            if s_channel.isChecked():
                                self._update_graph_widget((i,j))

            case "Correlation rate":
                print("test 2")
            case "Correlation histogram":
                print("Correlation histogram")
            case _: assert 0, "Unrechable"

    def _update_graph_widget(self,channels):
        print(channels)

    def _init_graph_widget(self,channels):
        # Test for the new RealTimeGraphWidget it will be remove
        line_setup = [
            GraphLineSetup(
                label=f"ch.",
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
        self.v_left_layout.addWidget(self.graph_widge) 
        
        