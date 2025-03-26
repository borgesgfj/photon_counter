#----------------------------------------------------------
"""
 Main Window use pyQT5
 
"""
#----------------------------------------------------------

from PyQt5 import QtGui
from PyQt5.QtWidgets import  QMainWindow

class MainWindow(QMainWindow):
    def __init__(
        *args,
        **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
