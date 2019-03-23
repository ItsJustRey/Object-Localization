# import the necessary packages
from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore

import sys
import GUI_Detection

import datetime
from datetime import datetime

app = QApplication(sys.argv)
widget = GUI_Detection.GUI_Detection()
widget.setWindowFlags(widget.windowFlags() |
        QtCore.Qt.WindowMinimizeButtonHint |
        QtCore.Qt.WindowMaximizeButtonHint|
        QtCore.Qt.WindowSystemMenuHint)

widget.show()
sys.exit(app.exec_())



