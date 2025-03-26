"""

The different Graph widget for the different kind of graph we want

"""


from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget



'''
Normal line Graph
'''
class RealTimeGraphsWidget(QWidget):
    def __init__(
        self,
        ):
        super().__init__()