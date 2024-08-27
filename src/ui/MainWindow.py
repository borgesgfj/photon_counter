from types import MethodType
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QComboBox, QCheckBox, QGroupBox, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget,QLineEdit,QFormLayout,QStackedLayout
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
coincidence_list = [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
font = QtGui.QFont("Times", 24, QtGui.QFont.Bold)

class MainWindow(QMainWindow):
    def __init__(
        self,
        timetagger_proxy,
        device_serial_number,
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

    def _init_right_layout(self):
        v_right_layout = QVBoxLayout()

        #Add a drop down menu to select the type of plot
        items = ["Single and Coincidence","Single count","Coincidence rate","Coincidence histogram",]
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
        self.box_last_value = QGroupBox("Last value")
        self.box_layout_last = QGridLayout()
        self.last_val = []
        self.box_last_value.setLayout(self.box_layout_last)
        v_right_layout.addWidget(self.box_last_value)

        #Add a 4 check box to selecte witch channels are ploted
        self.main_button_list = []
        box = QGroupBox("Main Channel")
        box_layout = QGridLayout()
        line = 0
        collum =0
        for channel in range(4 ):
            check = QCheckBox(f"ch {channel+1}")
            # if channel == 1 or channel == 2 : check.setChecked(True)
            check.setChecked(True)
            check.stateChanged.connect(self._show_graph)
            self.main_button_list += [check]
            box_layout.addWidget(check,line,collum)
            collum +=1
            if collum>1:
                line +=1
                collum =0
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)

        #Add checks box to selecte witch coincidence channels are ploted
        self.second_button_list = []
        box = QGroupBox("Second Channel")
        box_layout = QGridLayout()
        line = 0
        collum = 0
        for channel in coincidence_list:
            check = QCheckBox(f"ch {channel[0]}/{channel[1]}")
            # if channel == 0 or channel==2: check.setChecked(True)
            if line ==0:
                check.setChecked(True)
            check.stateChanged.connect(self._show_graph)
            self.second_button_list += [check]
            box_layout.addWidget(check,line,collum)
            collum +=1
            if collum >2:
                collum =0
                line+=1


        box.setLayout(box_layout)
        v_right_layout.addWidget(box)

        #Add refresh button
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._show_graph)
        v_right_layout.addWidget(refresh)

        #Add save button
        self.save =QPushButton("Save")
        self.save.clicked.connect(self.save_data)
        v_right_layout.addWidget(self.save)

        return v_right_layout
    #Initialize the main window
    def _init_interface(self):

        v_right_layout = self._init_right_layout()

        #Add a second page to the right layout to add a delay input
        main_r_box = QGroupBox()
        main_r_box.setLayout(v_right_layout)


        second_r_box = QGroupBox()
        second_r_box_layout = QFormLayout()
        self.selector_2 = QComboBox()
        self.selector_2.addItems(['1','2','3','4'])
        second_r_box_layout.addRow("Select Channel",self.selector_2)
        self.delay_input = QLineEdit()
        second_r_box_layout.addRow("Input delay",self.delay_input)

        button = QPushButton("Confirm")
        button.clicked.connect(self._add_delay)
        second_r_box_layout.addWidget(button)

        self.delay_list = []
        for i in range(4):
            label =QLabel()
            delay = self.timetagger_proxy.getInputDelay(i+1)
            label.setText(f"{delay}")
            self.delay_list += [label]
            second_r_box_layout.addRow(f"Ch{i+1}",label)
        second_r_box.setLayout(second_r_box_layout)


        # Set up the stack layout to change pages
        self.stack_layout = QStackedLayout()
        self.stack_layout.addWidget(main_r_box)
        self.stack_layout.addWidget(second_r_box)

        main_v_layout = QVBoxLayout()
        self.pageComboBox = QComboBox()
        self.pageComboBox.addItem("Page 1")
        self.pageComboBox.addItem("Page 2")
        self.pageComboBox.activated.connect(self.stack_layout.setCurrentIndex)

        main_v_layout.addWidget(self.pageComboBox)
        main_v_layout.addLayout(self.stack_layout)

        # Graph layout
        self.v_left_layout  = QVBoxLayout()
        self._show_graph()
        #Set up the main layout
        hlayout = QHBoxLayout()
        hlayout.addLayout(self.v_left_layout)
        hlayout.addLayout(main_v_layout)
        hlayout.setStretch(0, 4)
        hlayout.setStretch(1, 1)
        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)

    #Function that save the data
    def save_data(self):
        channel_list = []
        with open("save_data.txt","a") as f:
            for i,m_channel in enumerate(self.main_button_list):
                if m_channel.isChecked():
                    channel_list += [i+1]
            for channel in self.coincidence_list:
                channel_list += [channel.getChannels()[0]]
            counts = self.measurement_service.get_accumulated_count(channel_list,self.timetagger_proxy,30*10**12)
            for value in counts:
                f.write(f"{value},")
            f.write("\n")

    #Init the timer for the label widget that displya the last value
    def _init_last_timer(self):
        self.box_last_value.timer = QtCore.QTimer()
        self.box_last_value.timer.setInterval(GRAPH_ANIMATION_INTERVAL)
        self.box_last_value.timer.timeout.connect(self._update_last)
        self.box_last_value.timer.start()

    #Function that update the display of the last value
    def _update_last(self):
        for label in self.last_val:
            value = self.measurement_service.measurements_data.get_last_value(label[2])
            if value:
                if isinstance(value,tuple):
                    label[0].setText(label[1]+f": {value[0]},{value[1]}")
                else:
                    label[0].setText(label[1]+f": {int(value)}")


    def _add_delay(self):
        channel = self.selector_2.currentIndex()+1
        try :
            delay = int(self.delay_input.text())
            self.timetagger_proxy.setInputDelay(channel,delay)
            self.delay_list[channel-1].setText(f"{delay}")
        except :
            pass
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

        for label  in self.last_val:
            self.box_layout_last.removeWidget(label[0])
        self.last_val = []

        #Match case with the current text of the drop down menu
        match graph_type:
            case "Single count":
                self.selector_histo.setVisible(False)
                self.bin_params.setVisible(False)
                self.save.setVisible(True)
                self.coincidence_list = []
                self.update()
                self._update_graph_widget_single()

            case "Coincidence rate":
                self.bin_params.setVisible(False)
                self.selector_histo.setVisible(False)
                self.save.setVisible(True)
                self.update()
                self._update_graph_widget_coincidence()

            case "Coincidence histogram":
                self.selector_histo.setVisible(True)
                self.bin_params.setVisible(True)
                self.save.setVisible(False)
                self.coincidence_list = []

                self.update()

                for j,s_channel in enumerate(self.second_button_list):
                    if s_channel.isChecked():
                        self._update_graph_widget_histogram(coincidence_list[j])

            case "Single and Coincidence":
                self.selector_histo.setVisible(False)
                self.bin_params.setVisible(False)
                self.save.setVisible(True)

                self.update()
                self._update_graph_widget_single()
                self._update_graph_widget_coincidence()

            # case "Single and Histogram":
            #     self.selector_histo.setVisible(True)
            #     self.bin_params.setVisible(True)
            #     self.save.setVisible(False)
            #     self.coincidence_list = []
            #     self.update()
            #     self._update_graph_widget_single()
            #     for i,m_channel in enumerate(self.main_button_list):
            #         if m_channel.isChecked():
            #             for j,s_channel in enumerate(self.second_button_list):
            #                 if s_channel.isChecked():
            #                     if j!=i:
            #                         self._update_graph_widget_histogram([i+1,j+1])

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
                                color=color_list[color_count])]
                channel_list +=[i+1]
                color_count += 1
                if color_count > len(color_list)-1: color_count = 0
                label = QLabel()
                label.setFont(font)
                key=(i+1,MeasurementType.SINGLE_COUNTS)
                self.last_val += [(label,f"ch.{i+1}",key)]
                self.box_layout_last.addWidget(label)
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
        # channel_list =[]

        for j,s_channel in enumerate(self.second_button_list):
            if s_channel.isChecked():
                # if i != j and (j+1,i+1) not in channel_list : #select only if the channels are different, will need refactoring when we have two timetagger
                # channel_list += [(i+1,j+1)]
                line_setup += [ GraphLineSetup(
                                label=f"ch.{coincidence_list[j][0]}/{coincidence_list[j][1]}",
                                symbol="s",
                                color=color_list[color_count])]
                color_count += 1
                if color_count > len(color_list)-1: color_count = 0
                coincidence_virtual_channel = self.builder.build_coincidence_virtual_channel(self.timetagger_proxy, coincidence_list[j])
                self.coincidence_list += [coincidence_virtual_channel]
                v_channel_list += [coincidence_virtual_channel.getChannels()[0]]
                label = QLabel()
                label.setFont(font)
                key = (coincidence_virtual_channel.getChannels()[0],MeasurementType.COINCIDENCES)
                self.last_val += [(label,f" ch.{coincidence_list[j][0]}/{coincidence_list[j][1]}",key)]
                self.box_layout_last.addWidget(label)
        if v_channel_list != []:
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
                        color=Color.RED_PRIMARY)]
        histo_type = histogram_type[self.selector_histo.currentText()]
        param = CountRateReqParams(channels,self.device_serial_number,
                                    self.timetagger_proxy,histo_type )
        try :
            param.n_bin = int(self.n_bin_input.text())
            param.bin_width = int(self.bin_width_input.text())
            print("N bins",param.n_bin)
            print("Bins width",param.bin_width)
        except Exception as error:
            print(error)
        histo = self.builder.build_histogram_measurment(param)
        param.histogram_measurement = histo
        widget_info = WidgetInfo("Coincidence Count",line_setup,
                        "Count",Color.WHITE_PRIMARY,True)
        #widget = (w, param)
        graph_widget = RealTimeGraphsWidget(widget_info,param,measaurement_service = self.measurement_service)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)
        label = QLabel()
        key = (histo,histo_type)
        self.last_val += [(label,f" ch.{channels}",key)]
        self.box_layout_last.addWidget(label)
