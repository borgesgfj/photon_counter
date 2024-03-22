from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget,  QComboBox, QCheckBox, QGroupBox
from AppController import AppController
from ui.graphs.RealTimeGraphsWidget import RealTimeGraphsWidget
from time_tagger.measurement.service import MeasurementService , CountRateReqParams
from ui.styles import Color
from ui.graphs.GraphWidget2D import WidgetInfo, GraphLineSetup
from time_tagger.measurement.repository import MeasurementType
from time_tagger.builder import TimeTaggerBuilder

color_list = [Color.BLUE_PRIMARY,Color.GREEN_PRIMARY,Color.RED_PRIMARY,Color.BLACK]

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
        self.measurement_service = measurement_service
        self.graph_widget = None
        self.widget_list = []
        self.histo_list = []
        self.builder = TimeTaggerBuilder()
        self._init_interface()

    def _init_interface(self):
        self.v_left_layout  = QVBoxLayout()
        v_right_layout = QVBoxLayout()

        items = ["Single and Coincidence","Single count","Coincidence rate","Coincidence histogram"]
        self.selector = QComboBox()
        self.selector.addItems(items)
        self.selector.activated.connect(self._show_graph)
        v_right_layout.addWidget(self.selector)

        self.main_button_list = []
        box = QGroupBox("Main Channel")
        box_layout = QVBoxLayout()
        for channel in range(4):
            check = QCheckBox(f"ch {channel+1}")
            if channel == 0 or channel == 1 : check.setChecked(True)
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

        hlayout = QHBoxLayout()
        self._show_graph()
        hlayout.addLayout(self.v_left_layout)
        hlayout.addLayout(v_right_layout)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)


    #Switch case called when there is an update with the channels checked or the graph type chossen
    def _show_graph(self):
        graph_type = self.selector.currentText()
        match graph_type:
            case "Single count":
                for histo in self.histo_list:
                    histo.stop()
                for widget in self.widget_list:
                    self.v_left_layout.removeWidget(widget)
                    widget.timer.stop()
                    widget = None
                self.update()
                self.wiget_list = []
                self.measurement_service.measurements_data.clear()
                self._update_graph_widget_single()
            case "Coincidence rate":
                for histo in self.histo_list:
                    histo.stop()
                for widget in self.widget_list:
                    self.v_left_layout.removeWidget(widget)
                    widget.timer.stop()
                    widget = None
                self.update()
                self.wiget_list = []
                self.measurement_service.measurements_data.clear()
                self._update_graph_widget_coincidence()
            case "Coincidence histogram":
                for histo in self.histo_list:
                    histo.stop()
                for widget in self.widget_list:
                    self.v_left_layout.removeWidget(widget)
                    widget.timer.stop()
                    widget.close()
                self.update()
                self.wiget_list = []
                self.measurement_service.measurements_data.clear()
                for i,m_channel in enumerate(self.main_button_list):
                    if m_channel.isChecked():
                        for j,s_channel in enumerate(self.check_button_list):
                            if s_channel.isChecked():
                                if j!=i:
                                    self._update_graph_widget_histogram((i+1,j+1))
            case "Single and Coincidence":
                for histo in self.histo_list:
                    histo.stop()
                for widget in self.widget_list:
                    self.v_left_layout.removeWidget(widget)
                    widget.timer.stop()
                    widget.close()

                self.wiget_list = []
                self.measurement_service.measurements_data.clear()
                self._update_graph_widget_single()
                self._update_graph_widget_coincidence()
            case _: assert 0, "Unrechable"

    #Clear and update the graph for the single count rate
    def _update_graph_widget_single(self):
        line_setup = []
        channel_list = []
        #For now only the main channel is plot when we will have two time tagger we can have two wigdets
        color_count = 0
        for i,m_channel in enumerate(self.main_button_list):
            if m_channel.isChecked():
                line_setup += [ GraphLineSetup(
                label=f"ch.{i+1}",
                symbol="s",
                color=color_list[color_count],
                initial_data=[[[0.0], [0]]],)]
                channel_list +=[i+1]
                color_count += 1
                if color_count > len(color_list)-1: color_count = 0
        param = CountRateReqParams(channel_list,self.device_serial_number,self.timetagger_proxy,MeasurementType.SINGLE_COUNTS)
        w = WidgetInfo("Single Count",line_setup,
                        "Count/s",Color.WHITE_PRIMARY)
        widget = (w, param)
        graph_widget = RealTimeGraphsWidget([widget],measaurement_service= self.measurement_service)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)

    #Clear and update the graph for the coincidence count rate
    def _update_graph_widget_coincidence(self):
        line_setup = []
        color_count = 0
        self.coincidence_list = []
        v_channel_list = []
        for i,m_channel in enumerate(self.main_button_list):
            if m_channel.isChecked():
                for j,s_channel in enumerate(self.check_button_list):
                    if s_channel.isChecked():
                        if i != j:
                            channel_list = [i+1,j+1]
                            line_setup += [ GraphLineSetup(
                            label=f"ch.{i+1}/{j+1}",
                            symbol="s",
                            color=color_list[color_count],
                            initial_data=[[[0.0], [0]]],)]
                            color_count += 1
                            if color_count > len(color_list)-1: color_count = 0
                            coincidence_virtual_channel = self.builder.build_coincidence_virtual_channel(self.timetagger_proxy, channel_list)
                            self.coincidence_list += [coincidence_virtual_channel]
                            v_channel_list += [coincidence_virtual_channel.getChannels()[0]]
        print(v_channel_list)
        param = CountRateReqParams(v_channel_list,self.device_serial_number,self.timetagger_proxy,MeasurementType.COINCIDENCES)
        w = WidgetInfo("Coincidence Count",line_setup,
                        "Count/s",Color.WHITE_PRIMARY)
        widget = (w, param)
        graph_widget = RealTimeGraphsWidget([widget],measaurement_service= self.measurement_service)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)

    def _update_graph_widget_histogram(self,channels):
        line_setup = [ GraphLineSetup(
            label=f"ch.{channels}",
            symbol="s",
            color=Color.RED_PRIMARY,
            initial_data=[[[0.0], [0]]],)]

        histo = self.builder.build_histogram_measurment(self.timetagger_proxy, channels,MeasurementType.HISTOGRAM)
        self.histo_list  += [histo]
        param = CountRateReqParams(channels,self.device_serial_number,
                                    self.timetagger_proxy,MeasurementType.HISTOGRAM )
        param.histogram_measurement = histo
        w = WidgetInfo("Coincidence Count",line_setup,
                        "Count",Color.WHITE_PRIMARY,True)
        widget = (w, param)
        graph_widget = RealTimeGraphsWidget([widget],measaurement_service= self.measurement_service)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)
