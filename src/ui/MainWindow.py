from types import MethodType
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QComboBox, QCheckBox, QGroupBox, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget,QLineEdit,QFormLayout
from AppController import AppController
from ui.graphs.RealTimeGraphsWidget import RealTimeGraphsWidget
from time_tagger.measurement.service import MeasurementService , CountRateReqParams
from ui.styles import Color
from ui.graphs.GraphWidget2D import WidgetInfo, GraphLineSetup
from time_tagger.measurement.repository import MeasurementType
from time_tagger.builder import TimeTaggerBuilder
from shared.constants.constants import GRAPH_ANIMATION_INTERVAL
from PyQt5 import QtCore, QtGui


color_list = [Color.BLUE_PRIMARY,Color.GREEN_PRIMARY,Color.RED_PRIMARY,Color.BLACK]
histogram_type = {"Histogram": MeasurementType.HISTOGRAM,"Correlation":MeasurementType.HISTOGRAM_CORR}

font = QtGui.QFont("Times", 40, QtGui.QFont.Bold)

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
        self.timetagger_proxy = timetagger_proxy
        self.device_serial_number = device_serial_number
        self.measurement_service = measurement_service
        self.widget_list = []
        self.builder = TimeTaggerBuilder()
        self._init_interface()
        self._init_last_timer()

    #Initialize the main window
    def _init_interface(self):
        self.v_left_layout  = QVBoxLayout()
        v_right_layout = QVBoxLayout()

        #Add a drop down menu to select the type of plot
        items = ["Single count","Single and Coincidence","Coincidence histogram","Single count","Coincidence rate",]
        self.selector = QComboBox()
        self.selector.addItems(items)
        self.selector.activated.connect(self._show_graph)
        v_right_layout.addWidget(self.selector)

        #Add a drop down menu to select the type of histogram, only visible when the plot type is histogram
        self.selector_histo = QComboBox()
        self.selector_histo.addItems(histogram_type.keys())
        self.selector_histo.activated.connect(self._show_graph)
        v_right_layout.addWidget(self.selector_histo)
        self.selector_histo.setVisible(False)

        #Add input to change the number of bin and the bin width, only visible when the plot type is histogram
        self.bin_params =  QGroupBox("Bin params")
        layout =QFormLayout()
        self.n_bin_input = QLineEdit()
        self.bin_width_input =QLineEdit()
        layout.addRow("N bins", self.n_bin_input)
        layout.addRow("Bins width", self.bin_width_input)
        button = QPushButton("Update")
        button.clicked.connect(self._show_graph)
        layout.addWidget(button)
        self.bin_params.setLayout(layout)
        self.bin_params.setMaximumSize(200,100)
        v_right_layout.addWidget(self.bin_params)
        self.bin_params.setVisible(False)

        #Add a label widget that display the last value
        box = QGroupBox("Last value")
        box_layout = QGridLayout()
        self.max_val = QLabel()
        self.max_val.setFont(font)
        box_layout.addWidget(self.max_val)
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)

        #Add a 4 check box to selecte witch channels are ploted
        self.main_button_list = []
        box = QGroupBox("Main Channel")
        box_layout = QVBoxLayout()
        for channel in range(4 ):
            check = QCheckBox(f"ch {channel+1}")
            if channel == 0 or channel ==   1 : check.setChecked(True)
            check.stateChanged.connect(self._show_graph)
            self.main_button_list += [check]
            box_layout.addWidget(check)
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)

        #Add a 4 check box to selecte witch channels is used for the coincidence with the main channels
        self.check_button_list = []
        box = QGroupBox("Second Channel")
        box_layout = QVBoxLayout()
        for channel in range(4):
            check = QCheckBox(f"ch {channel+1}")
            if channel == 0: check.setChecked(True)
            check.stateChanged.connect(self._show_graph)
            self.check_button_list += [check]
            box_layout.addWidget(check)
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)

        #Add refresh button
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._show_graph)
        v_right_layout.addWidget(refresh)

        self.save =QPushButton("Save")
        self.save.clicked.connect(self.save_data)
        v_right_layout.addWidget(self.save)
        #Set up the layout
        hlayout = QHBoxLayout()
        self._show_graph()
        hlayout.addLayout(self.v_left_layout)
        hlayout.addLayout(v_right_layout)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)


    def save_data(self):
        print("Start save")
        self.save_timer = QtCore.QTimer()
        self.save_timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.save_timer.timeout.connect(self.measurement_service.measurements_data.save_data)
        self.save_timer.start(20*GRAPH_ANIMATION_INTERVAL)
    #Init the timer for the label widget that displya the last value
    def _init_last_timer(self):
        self.max_val.timer = QtCore.QTimer()
        self.max_val.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.max_val.timer.timeout.connect(self._update_last)
        self.max_val.timer.start()

    #Function that update the display of the last value
    def _update_last(self):
        last = self.measurement_service.measurements_data.get_last_value()
        last_str = ""
        for value in last :
            #TODO: add ratio between the average/max and the coincidence
            last_str += str(value)+"\n"
        self.max_val.setText(last_str)

    #Switch case called when there is an update with the channels checked or the graph type chossen
    def _show_graph(self):
        graph_type = self.selector.currentText()
        #clear the current widget
        for widget in self.widget_list:
            self.v_left_layout.removeWidget(widget)
            widget.timer.stop()
            widget.close()
        self.wiget_list = []
        self.measurement_service.measurements_data.clear()
        #Match case with the current text of the drop down menu
        match graph_type:
            case "Single count":
                self.selector_histo.setVisible(False)
                self.bin_params.setVisible(False)
                self.update()
                self._update_graph_widget_single()

            case "Coincidence rate":
                self.bin_params.setVisible(False)
                self.selector_histo.setVisible(False)
                self.update()
                self.wiget_list = []
                self._update_graph_widget_coincidence()

            case "Coincidence histogram":
                self.selector_histo.setVisible(True)
                self.bin_params.setVisible(True)
                self.update()
                for i,m_channel in enumerate(self.main_button_list):
                    if m_channel.isChecked():
                        for j,s_channel in enumerate(self.check_button_list):
                            if s_channel.isChecked():
                                if j!=i:
                                    self._update_graph_widget_histogram([i+1,j+1])

            case "Single and Coincidence":
                self.selector_histo.setVisible(False)
                self.bin_params.setVisible(False)
                self.update()
                self._update_graph_widget_single()
                self._update_graph_widget_coincidence()

            case "Single and Histogram":
                self.selector_histo.setVisible(True)
                self.bin_params.setVisible(True)
                self.update()
                self._update_graph_widget_single()
                for i,m_channel in enumerate(self.main_button_list):
                    if m_channel.isChecked():
                        for j,s_channel in enumerate(self.check_button_list):
                            if s_channel.isChecked():
                                if j!=i:
                                    self._update_graph_widget_histogram([i+1,j+1])

            case _: assert 0, "Unreachable"

    #Update the graph to the single count rate
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
                                initial_data=([0.0],[0]) )]
                channel_list +=[i+1]
                color_count += 1
                if color_count > len(color_list)-1: color_count = 0
        param = CountRateReqParams(channel_list,self.device_serial_number,self.timetagger_proxy,MeasurementType.SINGLE_COUNTS)
        widget_info = WidgetInfo("Single Count",line_setup,
                        "Count/s",Color.WHITE_PRIMARY)
        #widget = (w, param)
        graph_widget = RealTimeGraphsWidget(widget_info,param,measaurement_service= self.measurement_service)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)

    #Update the graph to the coincidence count rate
    def _update_graph_widget_coincidence(self):
        line_setup = []
        color_count = 0
        self.coincidence_list = []
        v_channel_list = []
        channel_list =[]
        for i,m_channel in enumerate(self.main_button_list):
            if m_channel.isChecked():
                for j,s_channel in enumerate(self.check_button_list):
                    if s_channel.isChecked():
                        if i != j and (j+1,i+1) not in channel_list : #select only if the channels are different, will need refactoring when we have two timetagger
                            channel_list += [(i+1,j+1)]
                            line_setup += [ GraphLineSetup(
                                            label=f"ch.{i+1}/{j+1}",
                                            symbol="s",
                                            color=color_list[color_count],
                                            initial_data=([0.0],[0]))]
                            color_count += 1
                            if color_count > len(color_list)-1: color_count = 0
                            coincidence_virtual_channel = self.builder.build_coincidence_virtual_channel(self.timetagger_proxy, [i+1,j+1])
                            self.coincidence_list += [coincidence_virtual_channel]
                            v_channel_list += [coincidence_virtual_channel.getChannels()[0]]
        param = CountRateReqParams(v_channel_list,self.device_serial_number,self.timetagger_proxy,
                                    MeasurementType.COINCIDENCES)
        widget_info = WidgetInfo("Coincidence Count",line_setup,
                        "Count/s",Color.WHITE_PRIMARY)

        graph_widget = RealTimeGraphsWidget(widget_info,param,measaurement_service= self.measurement_service)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)

    #Update the graph to a histogram
    def _update_graph_widget_histogram(self,channels):
        line_setup = [ GraphLineSetup(
                        label=f"ch.{channels}",
                        symbol="s",
                        color=Color.RED_PRIMARY,
                        initial_data=([0.0],[0]))]
        histo_type = histogram_type[self.selector_histo.currentText()]
        param = CountRateReqParams(channels,self.device_serial_number,
                                    self.timetagger_proxy,histo_type )
        try :
            param.n_bin = int(self.n_bin_input.text())
            param.bin_width = int(self.bin_width_input.text())
            print(param.n_bin,"\n",param.bin_width)
        except Exception as error:
            print(error)
        histo = self.builder.build_histogram_measurment(param)
        param.histogram_measurement = histo
        widget_info = WidgetInfo("Coincidence Count",line_setup,
                        "Count",Color.WHITE_PRIMARY,True)
        #widget = (w, param)
        graph_widget = RealTimeGraphsWidget(widget_info,param,measaurement_service= self.measurement_service)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)
