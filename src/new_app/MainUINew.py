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
        chan_number,
        *args,
        **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.timetagger_proxy = timetagger_proxy
        self.device_serial_number = device_serial_number
        self.chan_number = chan_number
        self.repo = MeasurementRepository()
        self.widget_list = []
        self.label_list = []

        self._init_interface()

    def _init_main_page(self):
        page_layout = QVBoxLayout()
        #Add a drop down menu to select the type of plot
        items = [Widget_Layout.SINGLE_COIN.value,Widget_Layout.HISTOGRAM.value,Widget_Layout.COIN_COUNT.value,Widget_Layout.MEASUREMENT.value]
        self.selector = QComboBox()
        self.selector.addItems(items)
        self.selector.activated.connect(self._show_graph)

        #Add a label widget that display the last value
        self.box_last_value = QGroupBox("Last value")
        self.box_layout_last = QGridLayout()
        self.box_last_value.setLayout(self.box_layout_last)
        page_layout.addWidget(self.box_last_value)

        histo_page = self._init_histo_page()

        #Add check boxes to selecte witch channels are ploted
        self.main_button_list = []
        self.main_chan_box = QGroupBox("Main Channel")
        box_layout = QGridLayout()
        line = 0
        collum = 0
        for channel in range(self.chan_number):
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
        self.main_chan_box.setLayout(box_layout)

        main_box = QGroupBox()
        self.first_stack_layout = QStackedLayout()
        self.first_stack_layout.addWidget(self.main_chan_box)
        self.first_stack_layout.addWidget(histo_page)
        main_box.setLayout(self.first_stack_layout)
        page_layout.addWidget(main_box)

        #Add checks box to selecte witch coincidence channels are ploted
        self.second_button_list = []
        self.coincidence_channels = []
        box = QGroupBox("Coincidences Channels")
        box_layout = QGridLayout()
        self.first_channel = QLineEdit()
        self.first_channel.setPlaceholderText("ch1-ch2,...")
        # self.second_channel = QComboBox()
        # self.second_channel.addItems([str(i) for i in range(1,chan_number+1)])
        box_layout.addWidget(self.first_channel,0,0)
        # box_layout.addWidget(self.second_channel,0,1)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_coin)
        box_layout.addWidget(add_button,0,1)
        button = QPushButton("show graph")
        button.clicked.connect(self._show_graph)
        box_layout.addWidget(button,1,0)
        button = QPushButton("clear")
        button.clicked.connect(self._clear_small_box)
        box_layout.addWidget(button,1,1)
        box.setLayout(box_layout)
        page_layout.addWidget(box)
        small_box =  QGroupBox()
        self.small_box_layout = QHBoxLayout()
        small_box.setLayout(self.small_box_layout)
        page_layout.addWidget(small_box)

        #Add refresh button
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._show_graph)
        page_layout.addWidget(refresh)

        #Add save button
        self.save =QPushButton("Save")
        self.save.clicked.connect(self.save_data)
        # page_layout.addWidget(self.save)
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
        page_layout.addWidget(self.save_box)
        self.save_box.setVisible(False)


        main_page = QGroupBox()
        main_page.setLayout(page_layout)
        return main_page

    def _init_histo_page(self):
        page_layout = QVBoxLayout()

        #Add a drop down menu to select the type of histogram, only visible when the plot type is histogram
        self.selector_histo = QComboBox()
        self.selector_histo.addItems(histogram_type.keys())
        self.selector_histo.activated.connect(self._show_graph)
        page_layout.addWidget(self.selector_histo)
        # self.selector_histo.setVisible(False)

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
        page_layout.addWidget(self.bin_params)
        # self.bin_params.setVisible(False)
        page_layout.addWidget(self.box_last_value)

        self.max_histo = QLineEdit()
        self.min_histo = QLineEdit()
        page_layout.addWidget(QLabel("Max"))
        page_layout.addWidget(self.max_histo)
        page_layout.addWidget(QLabel("Min"))
        page_layout.addWidget(self.min_histo)


        histo_page = QGroupBox()
        histo_page.setLayout(page_layout)

        return histo_page

    #Initialize the main window
    def _init_interface(self):
        #main rigth layout cointain the page

        main_page = self._init_main_page()

        #Add a second page to the right layout to add a delay input
        delay_box = QGroupBox()
        delay_box_layout = QFormLayout()
        self.selector_2 = QComboBox()
        self.selector_2.addItems([str(i+1) for i in range(self.chan_number)])
        delay_box_layout.addRow("Select Channel",self.selector_2)
        self.delay_input = QLineEdit()
        delay_box_layout.addRow("Input delay",self.delay_input)

        button = QPushButton("Confirm")
        button.clicked.connect(self._add_delay)
        delay_box_layout.addWidget(button)

        self.delay_list = []
        for i in range(self.chan_number):
            label =QLabel()
            delay = self.timetagger_proxy.getInputDelay(i+1)
            label.setText(f"{delay}")
            self.delay_list += [label]
            delay_box_layout.addRow(f"Ch{i+1}",label)
        delay_box.setLayout(delay_box_layout)



        # Set up the stack layout to change pages
        self.stack_layout = QStackedLayout()
        self.stack_layout.addWidget(main_page)
        self.stack_layout.addWidget(delay_box)

        main_v_layout = QVBoxLayout()
        self.pageComboBox = QComboBox()
        self.pageComboBox.addItem("Graph")
        # self.pageComboBox.addItem("Histogram")
        self.pageComboBox.addItem("Delay")
        self.pageComboBox.activated.connect(self.stack_layout.setCurrentIndex)

        main_v_layout.addWidget(self.pageComboBox)
        main_v_layout.addWidget(self.selector)
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
        try:
            text = self.first_channel.text()
            # j = int(self.second_channel.currentText())
            slip1 = text.split(",")
            for text  in slip1:
                i,j= text.split("-")
                i = int(i)
                j = int(j)
                if i > self.chan_number or j > self.chan_number :
                    pass
                else :
                    if i !=j and [i,j] not in self.coincidence_channels and [j,i] not in self.coincidence_channels:
                        self.coincidence_channels += [[i,j]]
                        label = QLabel()
                        label.setText(f"{i}-{j},")
                        self.small_box_layout.addWidget(label)
        except:
           pass

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
        self.first_stack_layout.setCurrentIndex(0)
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
        # self.bin_params.setVisible(False)
        # self.selector_histo.setVisible(False)
        #Match case with the current text of the drop down menu
        self.update()
        match graph_type:
            case Widget_Layout.SINGLE_COUNT.value:
                self.coincidence_list = []
                self._update_graph_widget_single(True)

            case Widget_Layout.COIN_COUNT.value:
                self._update_graph_widget_coincidence(True)

            case Widget_Layout.HISTOGRAM.value:
                # self.selector_histo.setVisible(True)
                # self.bin_params.setVisible(True)
                self.first_stack_layout.setCurrentIndex(1)
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

        try :
            max_histo = int(self.max_histo.text())
        except Exception as error:
            max_histo = None

        try :
            min_histo = int(self.min_histo.text())
        except Exception as error:
            min_histo = None

        if min_histo != None and max_histo != None:
            if min_histo > max_histo:
                c = min_histo
                min_histo = max_histo
                max_histo = c

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
        graph_widget = RealTimeHistoWidget(widget_info,param,self.repo,(label,f" ch.{channels[0]}-{channels[1]}",key),min_histo,max_histo)
        self.widget_list += [graph_widget]
        self.v_left_layout.addWidget(graph_widget)
