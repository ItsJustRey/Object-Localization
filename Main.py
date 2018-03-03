# import the necessary packages
#from tkinter import *
#from collections import deque
#import GUI

#from tkinter import *

#import OL_GUI as gui
#from PyQt5 import QtGui, uic
# PyQt5 import uic, QtWidgets


import sys
from PyQt5.QtWidgets import QApplication
import OL_GUI



app = QApplication(sys.argv)
widget = OL_GUI.OL_GUI()
widget.show()
sys.exit(app.exec_())

#def main():
#    # start the app
#   print("[INFO] starting...")
#    app = GUI.GUI()
#    app.mainloop()
#main()