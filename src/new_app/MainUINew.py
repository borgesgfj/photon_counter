from ast import Constant
import sys
from PyQt5 import QtWidgets,QtCore, QtGui
from PyQt5.QtWidgets import QDoubleSpinBox, QMainWindow, QGridLayout, QComboBox, QCheckBox, QGroupBox, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton,QLineEdit,QFormLayout,QStackedLayout, QWidget
from new_app.struct_and_enum import *
import new_app.Newbuilder as builder
from new_app.Newservice import MeasurementRepository
from new_app.NewGraph import RealTimeHistoWidget, RealTimeGraphsWidget
color_list = [Color.BLUE_PRIMARY,Color.GREEN_PRIMARY,Color.RED_PRIMARY,Color.BLACK]
histogram_type = {"Correlation":MeasurementType.HISTOGRAM_CORR,"Histogram": MeasurementType.HISTOGRAM,}
font = QtGui.QFont("Times", 24, QtGui.QFont.Bold)


class MainWindow(QMainWindow):
    def __init__(
        self,
        timetagger_proxy,
        device_serial_number,
        *args,
        **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.timetagger_proxy = timetagger_proxy
        self.device_serial_number = device_serial_number
        self.repo = MeasurementRepository()
        self.widget_list = []
        self.label_list = []

        self._init_interface()

    def _init_right_layout(self):
        v_right_layout = QVBoxLayout()
        chan_number = 16
        #Add a drop down menu to select the type of plot
        items = [Widget_Layout.SINGLE_COIN.value,Widget_Layout.SINGLE_COUNT.value,Widget_Layout.COIN_COUNT.value,Widget_Layout.MEASUREMENT.value,Widget_Layout.HISTOGRAM.value,]
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
        self.box_last_value.setLayout(self.box_layout_last)
        v_right_layout.addWidget(self.box_last_value)

        #Add a 4 check box to selecte witch channels are ploted
        self.main_button_list = []
        box = QGroupBox("Main Channel")
        box_layout = QGridLayout()
        line = 0
        collum = 0
        for channel in range(chan_number):
            check = QCheckBox(f"ch {channel+1}")
            if channel == 1 or channel == 0 : check.setChecked(True)
            #check.stateChanged.connect(self._show_graph)
            self.main_button_list += [check]
            box_layout.addWidget(check,line,collum)
            collum +=1
            if collum>3:
                line +=1
                collum =0
        button = QPushButton("Show Graph")
        button.clicked.connect(self._show_graph)
        box_layout.addWidget(button,line,collum)
        collum +=1
        button = QPushButton("Clear all")
        button.clicked.connect(self._clear_check_boxes)
        box_layout.addWidget(button,line,collum)
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)

        #Add checks box to selecte witch coincidence channels are ploted
        self.second_button_list = []
        self.coincidence_channels = []
        box = QGroupBox("Coincidences Channels")
        box_layout = QGridLayout()
        self.first_channel = QComboBox()

        self.first_channel.addItems([str(i) for i in range(1,chan_number+1)])
        self.second_channel = QComboBox()
        self.second_channel.addItems([str(i) for i in range(1,chan_number+1)])
        box_layout.addWidget(self.first_channel,0,0)
        box_layout.addWidget(self.second_channel,0,1)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_coin)
        box_layout.addWidget(add_button,0,2)
        button = QPushButton("refresh")
        button.clicked.connect(self._show_graph)
        box_layout.addWidget(button,1,1)
        button = QPushButton("clear")
        button.clicked.connect(self._clear_small_box)
        box_layout.addWidget(button,1,2)
        box.setLayout(box_layout)
        v_right_layout.addWidget(box)
        small_box =  QGroupBox()
        self.small_box_layout = QVBoxLayout()
        small_box.setLayout(self.small_box_layout)
        v_right_layout.addWidget(small_box)

        #Add refresh button
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._show_graph)
        v_right_layout.addWidget(refresh)

        #Add save button
        self.save =QPushButton("Save")
        self.save.clicked.connect(self.save_data)
        # v_right_layout.addWidget(self.save)
        # self.save.setVisible(False)
        self.measure_time = QDoubleSpinBox()
        self.measure_time.setRange(0.5,100)
        self.measure_time.setSingleStep(0.5)
        self.save_box =  QGroupBox("Save data")
        layout =QFormLayout()
        layout =QFormLayout()
        layout.addRow("Measurement Time(s)",self.measure_time)
        layout.addWidget(self.save)
        self.save_box.setLayout(layout)
        v_right_layout.addWidget(self.save_box)
        self.save_box.setVisible(False)

        return v_right_layout

    #Initialize the main window
    def _init_interface(self):
        #main rigth layout cointain the page
        main_r_box = QGroupBox()
        v_right_layout = self._init_right_layout()
        main_r_box.setLayout(v_right_layout)

        #Add a second page to the right layout to add a delay input
        second_r_box = QGroupBox()
        second_r_box_layout = QFormLayout()
        self.selector_2 = QComboBox()
        num_channels =8
        self.selector_2.addItems([str(i+1) for i in range(num_channels)])
        second_r_box_layout.addRow("Select Channel",self.selector_2)
        self.delay_input = QLineEdit()
        second_r_box_layout.addRow("Input delay",self.delay_input)

        button = QPushButton("Confirm")
        button.clicked.connect(self._add_delay)
        second_r_box_layout.addWidget(button)

        self.delay_list = []
        for i in range(num_channels):
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
        time =self.measure_time.value()*1E12
        with open("save_data.txt","a") as f:
            for widget in self.widget_list:
                if widget.widget_info.is_histogram:
                    key = (widget.param.channels,widget.param.measurement_type)
                    data = self.repo.get_datas(key,True)
                    f.write(f"{key}\n")
                    f.write(f"{data}")
                else:
                    counts = widget._update_plots(time)
                    for value in counts:
                        f.write(f"{value},")
            f.write("\n")

    # Add delay in a specfic channels
    def _add_delay(self):
        channel = self.selector_2.currentIndex()+1
        try :
            delay = int(self.delay_input.text())
            self.timetagger_proxy.setInputDelay(channel,delay)
            self.delay_list[channel-1].setText(f"{delay}")
        except :
            pass

    def _add_coin(self):
        i = int(self.first_channel.currentText())
        j = int(self.second_channel.currentText())
        if i !=j and [i,j] not in self.coincidence_channels and [j,i] not in self.coincidence_channels:
            self.coincidence_channels += [[i,j]]
            label = QLabel()
            label.setText(f"{i}-{j}")
            self.small_box_layout.addWidget(label)

    def  _clear_small_box(self):
        self.coincidence_channels = []
        while(self.small_box_layout.count()!= 0):
            widget = self.small_box_layout.itemAt(0).widget()
            self.small_box_layout.removeWidget(widget)


    def _clear_check_boxes(self):
        for box  in self.main_button_list:
            box.setChecked(False)

    #Update the graph
    def _show_graph(self):
        graph_type = self.selector.currentText()
        #clear the current widget
        for widget in self.widget_list:
            self.v_left_layout.removeWidget(widget)
            # widget.timer.stop()
            widget.close()
        self.widget_list = []
        self.repo.clear()

        for label  in self.label_list:
            self.box_layout_last.removeWidget(label)
        self.label_list= []
        self.save_box.setVisible(False)
        self.bin_params.setVisible(False)
        self.selector_histo.setVisible(False)
        #Match case with the current text of the drop down menu
        self.update()
        match graph_type:
            case Widget_Layout.SINGLE_COUNT.value:
                self.coincidence_list = []
                self._update_graph_widget_single(True)

            case Widget_Layout.COIN_COUNT.value:
                self._update_graph_widget_coincidence(True)

            case Widget_Layout.HISTOGRAM.value:
                self.selector_histo.setVisible(True)
                self.bin_params.setVisible(True)
                self.coincidence_list = []
                for coin in self.coincidence_channels:
                    self._update_graph_widget_histogram(coin)

            case Widget_Layout.SINGLE_COIN.value:
                self._update_graph_widget_single(True)
                self._update_graph_widget_coincidence(True)

            case Widget_Layout.MEASUREMENT.value:
                self.save_box.setVisible(True)
                self.update()
                self._update_graph_widget_single(False)
                self._update_graph_widget_coincidence(False)

            case _: assert 0, "Unreachable"

    #Update the graph to the single count rate
    def _update_graph_widget_single(self,has_timer):
        line_setup = []
        channel_list = []
        label_list = []
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
                label_list += [(label,f"ch.{i+1}",key)]
                self.box_layout_last.addWidget(label)
                self.label_list+=[label]
        param = CountRateReqParams(channel_list,self.device_serial_number,self.timetagger_proxy,MeasurementType.SINGLE_COUNTS)
        widget_info = WidgetInfo("Single Count",line_setup,
                        "Count/s",Color.WHITE_PRIMARY)
        graph_widget = RealTimeGraphsWidget(widget_info,param,self.repo,label_list,has_timer)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)

    #Update the graph to the coincidence count rate
    def _update_graph_widget_coincidence(self,has_timer):
        line_setup = []
        color_count = 0
        self.coincidence_list = []
        v_channel_list = []
        label_list = []

        for coin in self.coincidence_channels:
            line_setup += [ GraphLineSetup(
                            label=f"ch.{coin[0]}/{coin[1]}",
                            symbol="s",
                            color=color_list[color_count])]
            color_count += 1
            if color_count > len(color_list)-1: color_count = 0
            coincidence_virtual_channel = builder.build_coincidence_virtual_channel(self.timetagger_proxy,coin)
            self.coincidence_list += [coincidence_virtual_channel]
            v_channel_list += [coincidence_virtual_channel.getChannels()[0]]
            label = QLabel()
            label.setFont(font)
            key = (coincidence_virtual_channel.getChannels()[0],MeasurementType.COINCIDENCES)
            label_list += [(label,f" ch.{coin[0]}-{coin[1]}",key)]
            self.box_layout_last.addWidget(label)
            self.label_list+=[label]
        if v_channel_list != []:
            param = CountRateReqParams(v_channel_list,self.device_serial_number,self.timetagger_proxy,
                                        MeasurementType.COINCIDENCES)
            widget_info = WidgetInfo("Coincidence Count",line_setup,
                            "Count/s",Color.WHITE_PRIMARY)

            graph_widget = RealTimeGraphsWidget(widget_info,param,self.repo,label_list,has_timer)
            self.widget_list += [graph_widget]
            self.v_left_layout.addWidget(graph_widget)

    #Update the graph to a histogram
    def _update_graph_widget_histogram(self,channels):
        line_setup = GraphLineSetup(
                        label=f"ch.{channels[0]}/{channels[1]}",
                        symbol="s",
                        color=Color.RED_PRIMARY)
        histo_type = histogram_type[self.selector_histo.currentText()]
        param = CountRateReqParams(channels,self.device_serial_number,
                                    self.timetagger_proxy,histo_type )
        try :
            param.n_bin = int(self.n_bin_input.text())
            param.bin_width = int(self.bin_width_input.text())
        except Exception as error:
            print(error)
        self.n_bin_input.setText(f"{param.n_bin}")
        self.bin_width_input.setText(f"{param.bin_width}")
        histo = builder.build_histogram_measurment(param)
        param.histogram_measurement = histo
        widget_info = WidgetInfo("Coincidence Count",line_setup,
                        "Count",Color.WHITE_PRIMARY,True)

        label = QLabel()
        key = (histo,histo_type)
        self.box_layout_last.addWidget(label)
        self.label_list+=[label]
        graph_widget = RealTimeHistoWidget(widget_info,param,self.repo,(label,f" ch.{channels[0]}-{channels[1]}",key))
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)
