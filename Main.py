## import the necessary packages
import sys
from PyQt5.QtWidgets import QApplication

from pyqtgraph.Qt import QtGui, QtCore
import GUI_Detection

app = QApplication(sys.argv)
widget = GUI_Detection.GUI_Detection()
widget.setWindowFlags(widget.windowFlags() |
        QtCore.Qt.WindowMinimizeButtonHint |
        QtCore.Qt.WindowMaximizeButtonHint|
        QtCore.Qt.WindowSystemMenuHint)
widget.show()
sys.exit(app.exec_())


#def main():
#    # start the app
#   print("[INFO] starting...")
#    app = GUI.GUI()
#    app.mainloop()
#main()