import Object_Localization as Object_Localization

#
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog, QWidget, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from tkinter import *
import argparse
import cv2
import matplotlib
#matplotlib.use('TkAgg')
from PyQt5.uic.properties import QtWidgets, QtCore

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui, QtCore


import collections
import random
import time
import math
import numpy as np
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageTk
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from mpl_toolkits import mplot3d
import Object_Localization
from collections import deque

import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class OL_GUI(QDialog):
    def __init__(self):
        super(OL_GUI, self).__init__()

        loadUi('GUI_test.ui', self)

        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video", help="path to the (optional) video file")
        ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
        self.args = vars(ap.parse_args())

        self.v0_clear()



        self.image = None
        self.button_start.clicked.connect(self.start_video)
        self.button_stop.clicked.connect(self.stop_video)
        self.setup_plot()




    def start_video(self):
        print("start")
        self.video0 = cv2.VideoCapture(0)
        self.video0.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.video0.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)




        #self.plot_data()

    def update_frame(self):
        ret, self.frame = self.video0.read()

        (self.frame, self.v0_x, self.v0_y, self.v0_z, self.pts, self.counter, self.isDetected) = \
            Object_Localization.Object_Localization(self.frame, self.pts, self.counter)

        if (self.isDetected):
            if (len(self.pts) > 10):
                self.v0_xArray.append(self.v0_x)
                self.v0_yArray.append(self.v0_y)
                self.v0_zArray.append(self.v0_z)

        else:
            self.v0_clear()

        self.frame = cv2.flip(self.frame, 1)
        self.display_frame(self.frame, 1)

    def display_frame(self, _frame, window = 1):
        qformat = QImage.Format_Indexed8
        if len(_frame.shape) == 3:
            if _frame.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        outputImage = QImage(_frame, _frame.shape[1], _frame.shape[0], _frame.strides[0], qformat)
        outputImage = outputImage.rgbSwapped()

        if window == 1:
            self.label_video0.setPixmap(QPixmap.fromImage(outputImage))
            self.label_video0.setScaledContents(True)
            self.label_video1.setPixmap(QPixmap.fromImage(outputImage))
            self.label_video1.setScaledContents(True)
            self.label_video2.setPixmap(QPixmap.fromImage(outputImage))
            self.label_video2.setScaledContents(True)

    def stop_video(self):
        print("stop")
        self.timer.stop()

    def v0_clear(self):
        self.v0_xArray = []
        self.v0_yArray = []
        self.v0_zArray = []
        self.v0_x = None
        self.v0_y = None
        self.v0_z = None
        self.counter = 0
        self.pts = deque(maxlen=self.args["buffer"])
        return


    def setup_plot(self):

        w = gl.GLViewWidget()
        w.opts['distance'] = 40
        # w.show()
        w.setWindowTitle('pyqtgraph example: GLLinePlotItem')

        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        w.addItem(gz)

        def fn(x, y):
            return np.cos((x ** 2 + y ** 2) ** 0.5)

        n = 51
        y = np.linspace(-10, 10, n)
        x = np.linspace(-10, 10, 100)
        for i in range(n):
            yi = np.array([y[i]] * 100)
            d = (x ** 2 + yi ** 2) ** 0.5
            z = 10 * np.cos(d) / (d + 1)
            pts = np.vstack([x, yi, z]).transpose()
            plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i, n * 1.3)), width=(i + 1) / 10., antialias=True)
            w.addItem(plt)
        self.layout_plot.addWidget(w)

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()


class DynamicPlotter():

    def __init__(self, sampleinterval=0.1, timewindow=10.):
        # Data stuff
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y, pen=(255,0,0))
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def getdata(self):
        frequency = 0.5
        noise = random.normalvariate(0., 1.)
        new = 10.*math.sin(time.time()*frequency*2*math.pi) + noise
        return new

    def updateplot(self):
        self.databuffer.append( self.getdata() )
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        self.app.processEvents()

    def run(self):
        self.app.exec_()