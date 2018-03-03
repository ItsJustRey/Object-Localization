# import the necessary packages
from tkinter import *
from collections import deque
import GUI
import sys
from tkinter import *

import OL_GUI as gui
import PyQt5
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi

def main():
    app = QApplication(sys.argv)
    window = gui.OL_Main_Window()
    window.setWindowTitle("Test")
    window.show()
    sys.exit(app.exec_())

main()
#def main():
#    # start the app
#   print("[INFO] starting...")
#    app = GUI.GUI()
#    app.mainloop()
#main()