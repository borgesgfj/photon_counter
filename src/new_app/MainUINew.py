#----------------------------------------------------------
"""
 Main Window use pyQT5
 
"""
#----------------------------------------------------------

from PyQt5 import QtGui
from PyQt5.QtWidgets import  QMainWindow
from new_app.constants import Color_List, Widget_Layout,MeasurementType
from new_app.NewGraph import RealTimeGraphsWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedLayout, QGridLayout,QFormLayout
from PyQt5.QtWidgets import  QWidget, QComboBox, QGroupBox, QCheckBox,QPushButton, QLineEdit,QDoubleSpinBox,QLabel


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
        self.selector_histo.setVisible(False)   


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
        # add_button.clicked.connect(self._add_coin)
        box_layout.addWidget(add_button,0,1)
        button = QPushButton("clear")
        # button.clicked.connect(self._clear_small_box)
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


    def _init_graphs_widget(self):
        self.save_box.setVisible(False)
        self.histo_params.setVisible(False)
        