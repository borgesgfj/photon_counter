#----------------------------------------------------------
"""
 Main Window use pyQT5
 
"""
#----------------------------------------------------------

from PyQt5 import QtGui
from PyQt5.QtWidgets import  QMainWindow
from new_app.constants import Colot_List
from new_app.NewGraph import RealTimeGraphsWidget

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