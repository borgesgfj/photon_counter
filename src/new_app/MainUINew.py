#----------------------------------------------------------
"""
 Main Window use pyQT5
 
"""
#----------------------------------------------------------

from PyQt5 import QtGui
from PyQt5.QtWidgets import  QMainWindow
from new_app.constants import Color_List, Widget_Layout,MeasurementType,CountRateReqParams,WidgetInfo,Color,GraphLineSetup
from new_app.NewGraph import RealTimeGraphsWidget,ThreadHistoWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedLayout, QGridLayout,QFormLayout
from PyQt5.QtWidgets import  QWidget, QComboBox, QGroupBox, QCheckBox,QPushButton, QLineEdit,QDoubleSpinBox,QLabel
from new_app.NewService import MeasurementRepository
import new_app.NewBuilder as builder
font = QtGui.QFont("Times", 20, QtGui.QFont.Bold) #font for the last value labels

class MainWindow(QMainWindow):
    def __init__(
        self,
        device_serial_number,
        timetagger_proxy,
        chan_number,
        *args,
        **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.device_serial_number = device_serial_number
        self.timetagger_proxy= timetagger_proxy 
        self.chan_number = chan_number
        self.coincidence_channels = [] #Contait tuple of channel for coincidence ( EX : (1,3) ) 
        self.coincidence_id_list = [] #Cointait the coincidence virtual channels from time tagger
        self.widget_list = []
        self.label_list = []
        self.repo = MeasurementRepository()
        self._init_interface()
    
    
    
    def _init_interface(self):
        main_layout = QHBoxLayout() 
        main_widget = QWidget()  
        
        self.graph_layout = QVBoxLayout() 
        main_layout.addLayout(self.graph_layout)
        
        
        self.param_layout_pages = self._init_param_layout()
        
        self.param_layout_main = QVBoxLayout()
        self.pageComboBox = QComboBox()
        self.pageComboBox.addItem("Graph")
        self.pageComboBox.addItem("Delay")
        self.pageComboBox.activated.connect(self.param_layout_pages.setCurrentIndex)
        self.param_layout_main.addWidget(self.pageComboBox)
        self.param_layout_main.addLayout(self.param_layout_pages)
        main_layout.addLayout(self.param_layout_main) 
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self._init_graphs_widget()



    # init the layout on the right of the application that contain all the parameter
    def _init_param_layout(self):
        param_layout_main = QStackedLayout()
        
        #First page 
        
        first_page_layout = QVBoxLayout()
        
        #select the kind of graph to display
        items = [Widget_Layout.SINGLE_COIN.value,Widget_Layout.HISTOGRAM.value,Widget_Layout.MEASUREMENT.value]
        self.selector = QComboBox()
        self.selector.addItems(items)
        self.selector.activated.connect(self._init_graphs_widget)
        first_page_layout.addWidget(self.selector)

        #select the kind of histogram to display
        self.selector_histo = QComboBox()
        self.selector_histo.addItems([MeasurementType.HISTOGRAM.value,MeasurementType.HISTOGRAM_CORR.value])
        self.selector_histo.activated.connect(self._init_graphs_widget)
        first_page_layout.addWidget(self.selector_histo) 
         


        #Add a label widget that display the last value
        self.box_last_value = QGroupBox("Last value")
        self.box_layout_last = QVBoxLayout()
        self.box_last_value.setLayout(self.box_layout_last)
        first_page_layout.addWidget(self.box_last_value)
        #--------------------------------------------------------

        #Add check boxes to selecte witch channels are ploted
        self.main_button_list = []
        self.main_chan_box = QGroupBox("Main Channel")
        box_layout = QGridLayout()
        line = 0
        collum = 0
        for channel in range(self.chan_number):
            check = QCheckBox(f"ch {channel+1}")
            if channel == 1 or channel == 0 : check.setChecked(True)
            self.main_button_list += [check]
            box_layout.addWidget(check,line,collum)
            collum +=1
            if collum>3:
                line +=1
                collum =0
        line +=1
        button = QPushButton("Show Graph")
        button.clicked.connect(self._init_graphs_widget)
        box_layout.addWidget(button,line,collum)
        collum +=1
        button = QPushButton("Clear all")
        # button.clicked.connect(self._clear_check_boxes)
        box_layout.addWidget(button,line,collum)

        self.main_chan_box.setMaximumHeight(200) 
        self.main_chan_box.setLayout(box_layout)

        first_page_layout.addWidget(self.main_chan_box)
        #--------------------------------------------------------

        #Add input to change the number of bin and the bin width, only visible when the plot type is histogram
        self.histo_params =  QGroupBox("Bin params")
        layout =QFormLayout()
        self.n_bin_input = QLineEdit()
        self.n_bin_input.setPlaceholderText("200")
        self.bin_width_input =QLineEdit()
        self.bin_width_input.setPlaceholderText("50")
        self.max_histo = QLineEdit()
        self.min_histo = QLineEdit()
        layout.addRow("N bins", self.n_bin_input)
        layout.addRow("Bins width", self.bin_width_input)
        layout.addRow("Max",self.max_histo)
        layout.addRow("Min",self.min_histo)
        button = QPushButton("Update")
        button.clicked.connect(self._init_graphs_widget)
        layout.addWidget(button)
        self.histo_params.setMaximumHeight(200) 
        self.histo_params.setLayout(layout)
        
        first_page_layout.addWidget(self.histo_params)
        
        #--------------------------------------------------------

        #Add input to selecte witch coincidence channels are ploted
        box = QGroupBox("Coincidences Channels")
        box_layout = QGridLayout()
        self.first_channel = QLineEdit()
        self.first_channel.setPlaceholderText("ch1-ch2,...")
        box_layout.addWidget(self.first_channel,0,0)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_coincidence)
        box_layout.addWidget(add_button,0,1)
        button = QPushButton("clear")
        button.clicked.connect(self._clear_coincidence_list)
        box_layout.addWidget(button,3,0)
        small_box =  QGroupBox()
        self.small_box_layout = QHBoxLayout()
        small_box.setLayout(self.small_box_layout)
        box_layout.addWidget(small_box)
        box.setLayout(box_layout)
        box.setMaximumHeight(200)
        first_page_layout.addWidget(box)

        #--------------------------------------------------------
        #Add refresh button
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._init_graphs_widget)
        first_page_layout.addWidget(refresh)
        first_page_widget = QWidget()
       
        #--------------------------------------------------------
        #Add save button 
        self.save_box =  QGroupBox("Save data")
        layout =QFormLayout()        
        # Spin box to select the integration time of the save, min 0.5s max 100s step 0.5s
        self.measure_time = QDoubleSpinBox()
        self.measure_time.setRange(0.5,100) 
        self.measure_time.setSingleStep(0.5)
        layout.addRow("Measurement Time(s)",self.measure_time)
        self.save =QPushButton("Save")
        # self.save.clicked.connect(self.save_data)
        layout.addWidget(self.save)
        self.save_box.setMaximumHeight(100)
        self.save_box.setLayout(layout)
        first_page_layout.addWidget(self.save_box)
        
        #--------------------------------------------------------
       
        first_page_widget.setMaximumWidth(400)
        first_page_widget.setLayout(first_page_layout)

        param_layout_main.addWidget(first_page_widget)


        #--------------------------------------------------------
        #--------------------------------------------------------

        #Second page 
        #Change the delay

        delay_box = QGroupBox()
        delay_box_layout = QFormLayout()
        self.selector_2 = QComboBox()
        self.selector_2.addItems([str(i+1) for i in range(self.chan_number)])
        delay_box_layout.addRow("Select Channel",self.selector_2)
        self.delay_input = QLineEdit()
        delay_box_layout.addRow("Input delay",self.delay_input)

        button = QPushButton("Confirm")
        # button.clicked.connect(self._add_delay)
        delay_box_layout.addWidget(button)

        self.delay_list = []
        for i in range(self.chan_number):
            label =QLabel()
            delay = self.timetagger_proxy.getInputDelay(i+1)
            label.setText(f"{delay}")
            self.delay_list += [label]
            delay_box_layout.addRow(f"Ch{i+1}",label)
        delay_box.setLayout(delay_box_layout)

        param_layout_main.addWidget(delay_box)
        #--------------------------------------------------------

        return param_layout_main

    def _add_coincidence(self):
        try:
            text = self.first_channel.text()
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
    def _clear_coincidence_list(self):
        self.coincidence_channels = []
        while(self.small_box_layout.count()!= 0):
            widget = self.small_box_layout.itemAt(0).widget()
            self.small_box_layout.removeWidget(widget)

    def _init_graphs_widget(self):
        self.save_box.setVisible(False)
        self.histo_params.setVisible(False)
        self.selector_histo.setVisible(False) 
        self.main_chan_box.setVisible(True)
        graph_type = self.selector.currentText()
        #clear the current widget
        for widget in self.widget_list:
            try: 
                widget.thread.terminate()
                widget.thread.wait()
            except:
                pass
            self.graph_layout.removeWidget(widget)
            widget.close()
            del widget
        self.widget_list = []
        self.repo.clear()

        for label  in self.label_list:
            self.box_layout_last.removeWidget(label)
            label.close()
            del label
        self.label_list= []
        self.update()
        match graph_type:
            case Widget_Layout.SINGLE_COIN.value:
                self.single_count_graph(True)
                self.coincidence_count_graph(True)
            case Widget_Layout.HISTOGRAM.value:
                self.main_chan_box.setVisible(False)
                self.histo_params.setVisible(True)
                self.selector_histo.setVisible(True)
                for coin in self.coincidence_channels:
                    self.histogram_graph(coin)
            case _ :
                print("Not implemented yet")
                    
    def single_count_graph(self,has_timer):
        line_setup = []
        channel_list = []
        label_list = []
        color_count = 0
        for i,m_channel in enumerate(self.main_button_list):
            if m_channel.isChecked():
                line_setup += [ GraphLineSetup(
                                label=f"ch.{i+1}",
                                symbol="s",
                                color=Color_List[color_count])]
                channel_list +=[i+1]
                color_count += 1
                if color_count > len(Color_List)-1: color_count = 0
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
        self.graph_layout.addWidget(graph_widget)

    def coincidence_count_graph(self,has_timer):
        line_setup = []
        color_count = 0
        self.coincidence_list = []
        v_channel_list = []
        label_list = []
        for coin in self.coincidence_channels:
            line_setup += [ GraphLineSetup(
                            label=f"ch.{coin[0]}/{coin[1]}",
                            symbol="s",
                            color=Color_List[color_count])]
            color_count += 1
            if color_count > len(Color_List)-1: color_count = 0
            coincidence_virtual_channel = builder.build_coincidence_virtual_channel(self.timetagger_proxy,coin)
            self.coincidence_id_list += [coincidence_virtual_channel]
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
            self.graph_layout.addWidget(graph_widget)


    def histogram_graph(self,channels):
        line_setup = GraphLineSetup(
                        label=f"ch.{channels[0]}/{channels[1]}",
                        symbol="s",
                        color=Color.RED_PRIMARY)
        match self.selector_histo.currentText():
            case MeasurementType.HISTOGRAM.value:
                histo_type =  MeasurementType.HISTOGRAM
            case _ :
                 histo_type =  MeasurementType.HISTOGRAM_CORR

        param = CountRateReqParams(channels,self.device_serial_number,
                                    self.timetagger_proxy,histo_type )
        #parse the min and max maybe should be a separate function
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
        self.box_layout_last.addWidget(label)
        self.label_list+=[label]
        graph_widget = ThreadHistoWidget(widget_info,param,self.repo,(label,f" ch.{channels[0]}-{channels[1]}"),min_histo,max_histo)
        self.widget_list += [graph_widget]
        self.graph_layout.addWidget(graph_widget)