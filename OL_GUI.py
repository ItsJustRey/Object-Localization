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

        loadUi('GUI.ui', self)
        self.showMaximized()

        ap = argparse.ArgumentParser()
        ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
        self.args = vars(ap.parse_args())
        self.image = None

        self.clear()
        self.button_start.clicked.connect(self.start_video)
        self.button_stop.clicked.connect(self.stop_video)
        self.button_clear.clicked.connect(self.clear)

        self.plot = OL_3D_Plot(self)
        self.layout_plot.addWidget(self.plot)


    # INITIALIZE VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def start_video(self):
        print("start")

        # INITIALIZE VIDEO 0 FRAMES AND DATA
        self.video0 = cv2.VideoCapture(0)
        self.video0.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.video0.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
        #self.v0_xArray = self.v0_yArray = self.v0_zArray = []
        #self.v0_x = self.v0_y = self.v0_z = None

        # INITIALIZE VIDEO 1 FRAMES AND DATA
        # self.video1 = cv2.VideoCapture(0)
        # self.video1.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        # self.video1.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
        # self.v1_xArray = self.v1_yArray = self.v1_zArray = []
        # self.v1_x = self.v1_y = self.v1_z = None

        # INITIALIZE VIDEO 2 FRAMES AND DATA
        # self.video2 = cv2.VideoCapture(0)
        # self.video2.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        # self.video2.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
        # self.v2_xArray = self.v2_yArray = self.v2_zArray = []
        # self.v2_x = self.v2_y = self.v2_z = None


        # CREATE TIMER THREAD TO UPDATE FRAME EVERY (x) milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

    # GET VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def update_frame(self):
        ret, self.v0_frame = self.video0.read()
        #ret, self.v1_frame = self.video1.read()
        #ret, self.v2_frame = self.video2.read()

        # VIDEO 0 OBJECT DETECTION returns data of given frame
        (self.v0_frame, self.v0_x, self.v0_y, self.v0_z, self.v0_pts, self.v0_counter, self.v0_isDetected) = \
            Object_Localization.Object_Localization(self.v0_frame, self.v0_pts, self.v0_counter)

        # VIDEO 1 OBJECT DETECTION returns data of given frame
        #(self.v1_frame, self.v1_x, self.v1_y, self.v1_z, self.v1_pts, self.v1_counter, self.v1_isDetected) = \
        #    Object_Localization.Object_Localization(self.v0_frame, self.v1_pts, self.v1_counter)

        # VIDEO 2 OBJECT DETECTION returns data of given frame
        #(self.v2_frame, self.v2_x, self.v2_y, self.v2_z, self.v2_pts, self.v2_counter, self.v2_isDetected) = \
        #    Object_Localization.Object_Localization(self.v2_frame, self.v2_pts, self.v2_counter)

        if (self.v0_isDetected):
            if (len(self.v0_pts) > 10):
                self.v0_xArray.append(self.v0_x)
                self.v0_yArray.append(self.v0_y)
                self.v0_zArray.append(self.v0_z)

            # if (len(self.v1_pts) > 10):
            #     self.v1_xArray.append(self.v1_x)
            #     self.v1_yArray.append(self.v1_y)
            #     self.v1_zArray.append(self.v1_z)

            # if (len(self.v2_pts) > 10):
            #     self.v2_xArray.append(self.v2_x)
            #     self.v2_yArray.append(self.v2_y)
            #     self.v2_zArray.append(self.v2_z)

        else:
            self.clear()


        # USE NUMPY TO COMBINE v0
        self.v0_xyz = np.vstack([self.v0_xArray, self.v0_yArray, self.v0_zArray]).transpose()
        #self.v1_xyz = np.vstack([self.v1_xArray, self.v1_yArray, self.v1_zArray]).transpose()
        #self.v2_xyz = np.vstack([self.v2_xArray, self.v2_yArray, self.v2_zArray]).transpose()
        self.plot.traces.setData(pos = self.v0_xyz)


        self.v0_frame = cv2.flip(self.v0_frame, 1)
        self.display_frame(self.v0_frame, 1)


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


    # USED TO CLEAR VIDEO 0, VIDEO 1, VIDEO 2 DATA STRUCTURES
    def clear(self):

        # CLEAR VIDEO 0 DATA STRUCTURES
        self.v0_xArray = []; self.v0_yArray = []; self.v0_zArray = []
        self.v0_x = None; self.v0_y = None; self.v0_z = None
        self.v0_counter = 0
        self.v0_pts = deque(maxlen=self.args["buffer"])

        # CLEAR VIDEO 1 DATA STRUCTURES
        # self.v1_xArray = self.v1_yArray = self.v1_zArray = []
        # self.v1_x = self.v1_y = self.v1_z = None
        # self.v1_counter = 0
        # self.v1_pts = deque(maxlen=self.args["buffer"])

        # CLEAR VIDEO 2 DATA STRUCTURES
        # self.v2_xArray = self.v2_yArray = self.v2_zArray = []
        # self.v2_x = self.v2_y = self.v2_z = None
        # self.v2_counter = 0
        # self.v2_pts = deque(maxlen=self.args["buffer"])

        return

# OPENGL 3D PLOT WIDGET
class OL_3D_Plot(QtGui.QWidget):
    def __init__(self, parent=None):
        super(OL_3D_Plot, self).__init__(parent)

        layout = QtGui.QHBoxLayout()

        self.plot = gl.GLViewWidget()
        self.plot.opts['distance'] = 2000
        self.plot.setWindowTitle('3-Dimensional Plot')
        self.plot.opts['fov'] = 1
        #self.plot.setGeometry(0, 110, 1920, 1080)
        #self.plot.show()

        # create the background grids
        gx = gl.GLGridItem(color = "b")
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)

        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)

        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)

        #gx.scale(1, 0.1, 0.1)
        #gy.scale(0.2, 0.1, 0.1)
        #gz.scale(0.1, 0.2, 0.1)

        self.plot.addItem(gx)
        self.plot.addItem(gy)
        self.plot.addItem(gz)
        self.plot.showMaximized()
        #pts = np.vstack(0, 0 ,0).transpose()
        #traces= gl.GLLinePlotItem(pos=pts)
        #self.plot.addItem(traces)
        v0_xArray = []
        v0_yArray = []
        v0_zArray = []
        #self.plot.resizeGL(400,400)
        plot_xyz = np.vstack([v0_xArray, v0_yArray, v0_zArray]).transpose()
        # self.curve = self.plot.plot.getPlotItem().plot()
        self.traces = gl.GLLinePlotItem(pos=plot_xyz)
        self.plot.addItem(self.traces)

        layout.addWidget(self.plot)
        self.setLayout(layout)
