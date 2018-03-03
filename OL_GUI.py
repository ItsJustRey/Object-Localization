
import PyQt5
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi

class OL_Main_Window(QDialog):
    def __init(self):
        super(OL_Main_Window, self).__init__()
        loadUi('untitled.ui', self)