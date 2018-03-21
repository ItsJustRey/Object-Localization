
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
# matplotlib.use('TkAgg')
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
        #self.showMaximized()

        ap = argparse.ArgumentParser()
        ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
        self.args = vars(ap.parse_args())
        self.image = None

        # CLEAR DATA STRUCTURES
        self.clear()

        # INITIALLY HIDE STOP/CLEAR
        self.button_stop.hide()
        self.button_clear.hide()

        # DEFINE BUTTON CLICK EVENTS
        self.button_start.clicked.connect(self.start_video)
        self.button_stop.clicked.connect(self.stop_video)
        self.button_clear.clicked.connect(self.clear)

        # SET UP 3D PLOT
        self.plot_v0 = OL_3D_Plot(self)
        #self.plot1 = OL_3D_Plot(self)
        #self.plot2 = OL_3D_Plot(self)
        #self.plot3 = OL_3D_Plot(self)
        self.layout_plot.addWidget(self.plot_v0)
        #self.layout_plot.addWidget(self.plot1)
        #self.layout_plot.addWidget(self.plot2)
        #self.layout_plot.addWidget(self.plot3)

        # INITIAL VIDEO SOURCES (SUBJECT TO CHANGE BY USER)
        self.VIDEO_SOURCE_0 = 0
        self.VIDEO_SOURCE_1 = 1
        self.VIDEO_SOURCE_2 = 2

        # COMBO BOXES
        comboBoxOptions = ["0", "1", "2"]
        self.comboBox_video0.addItems(comboBoxOptions)
        self.comboBox_video1.addItems(comboBoxOptions)
        self.comboBox_video2.addItems(comboBoxOptions)
        self.comboBox_video0.currentTextChanged.connect(self.comboBox_video0_changed)
        self.comboBox_video1.currentTextChanged.connect(self.comboBox_video1_changed)
        self.comboBox_video2.currentTextChanged.connect(self.comboBox_video2_changed)



    def comboBox_video0_changed(self):
        self.VIDEO_SOURCE_0 = self.comboBox_video0.currentText()

    def comboBox_video1_changed(self):
        self.VIDEO_SOURCE_1 = self.comboBox_video1.currentText()

    def comboBox_video2_changed(self):
        self.VIDEO_SOURCE_2 = self.comboBox_video2.currentText()

    # INITIALIZE VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def start_video(self):

        # HIDE/SHOW GUI ELEMENTS
        self.button_start.hide()
        self.button_stop.show()
        self.button_clear.show()
        self.comboBox_video0.hide()
        self.comboBox_video1.hide()
        self.comboBox_video2.hide()
        self.label_comboBox_video0.hide()
        self.label_comboBox_video1.hide()
        self.label_comboBox_video2.hide()

        # INITIALIZE VIDEO 0 FRAMES AND DATA
        self.video0 = cv2.VideoCapture(int(self.VIDEO_SOURCE_0))
        self.video0.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.video0.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

        # CREATE TIMER THREAD TO UPDATE FRAME EVERY (x) milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)


    # GET VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def update_frame(self):
        ret, self.v0_frame = self.video0.read()
        # ret, self.v1_frame = self.video1.read()
        # ret, self.v2_frame = self.video2.read()

        # VIDEO 0 OBJECT DETECTION returns data of given frame
        (self.v0_frame,
         self.v0_x_red, self.v0_y_red, self.v0_z_red, \
         self.v0_x_green, self.v0_y_green, self.v0_z_green, \
         self.v0_x_blue, self.v0_y_blue, self.v0_z_blue, \
         self.v0_x_yellow, self.v0_y_yellow, self.v0_z_yellow,
         self.v0_pts, self.v0_counter, self.v0_isRedDetected, self.v0_isGreenDetected, self.v0_isBlueDetected, self.v0_isYellowDetected) = \
            Object_Localization.Object_Localization(self.v0_frame, self.v0_pts, self.v0_counter)

        if (self.v0_isRedDetected):
            if (len(self.v0_pts) > 10):
                self.v0_red_xArray.append(self.v0_x_red)
                self.v0_red_yArray.append(self.v0_y_red)
                self.v0_red_zArray.append(self.v0_z_red)

        elif (self.v0_isGreenDetected):
          if (len(self.v0_pts) > 10):
                self.v0_green_xArray.append(self.v0_x_green)
                self.v0_green_yArray.append(self.v0_y_green)
                self.v0_green_zArray.append(self.v0_z_green)

        elif (self.v0_isBlueDetected):
            if (len(self.v0_pts) > 10):
                self.v0_blue_xArray.append(self.v0_x_blue)
                self.v0_blue_yArray.append(self.v0_y_blue)
                self.v0_blue_zArray.append(self.v0_z_blue)

        elif (self.v0_isYellowDetected):
            if (len(self.v0_pts) > 10):
                self.v0_yellow_xArray.append(self.v0_x_yellow)
                self.v0_yellow_yArray.append(self.v0_y_yellow)
                self.v0_yellow_zArray.append(self.v0_z_yellow)

        else:
            self.clear()

        # USE NUMPY TO COMBINE V0
        self.v0_red_xyz = np.vstack([self.v0_red_xArray, self.v0_red_yArray, self.v0_red_zArray]).transpose()
        self.v0_green_xyz = np.vstack([self.v0_green_xArray, self.v0_green_yArray, self.v0_green_zArray]).transpose()
        self.v0_blue_xyz = np.vstack([self.v0_blue_xArray, self.v0_blue_yArray, self.v0_blue_zArray]).transpose()
        self.v0_yellow_xyz = np.vstack([self.v0_yellow_xArray, self.v0_yellow_yArray, self.v0_yellow_zArray]).transpose()

        # V0 PLOT MULTIPLE TRACES
        self.plot_v0.trace_red.setData(pos=self.v0_red_xyz)
        self.plot_v0.trace_green.setData(pos=self.v0_green_xyz)
        self.plot_v0.trace_blue.setData(pos=self.v0_blue_xyz)
        self.plot_v0.trace_yellow.setData(pos=self.v0_yellow_xyz)

        self.v0_frame = cv2.flip(self.v0_frame, 1)
        self.display_frame(self.v0_frame, 1)

    def display_frame(self, _frame, window=1):
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

        # HIDE/SHOW GUI ELEMENTS
        self.button_start.show()
        self.button_stop.hide()
        self.button_clear.hide()
        self.comboBox_video0.show()
        self.comboBox_video1.show()
        self.comboBox_video2.show()
        self.label_comboBox_video0.show()
        self.label_comboBox_video1.show()
        self.label_comboBox_video2.show()

        # STOP TIMER THREAD AND RELEASE V0
        self.timer.stop()
        self.video0.release()

        # USED TO CLEAR VIDEO 0, VIDEO 1, VIDEO 2 DATA STRUCTURES
    def clear(self):
        print("clearing");
        # CLEAR VIDEO 0 DATA STRUCTURES
        self.v0_red_xArray = []
        self.v0_red_yArray = []
        self.v0_red_zArray = []
        self.v0_green_xArray = []
        self.v0_green_yArray = []
        self.v0_green_zArray = []
        self.v0_blue_xArray = []
        self.v0_blue_yArray = []
        self.v0_blue_zArray = []
        self.v0_yellow_xArray = []
        self.v0_yellow_yArray = []
        self.v0_yellow_zArray = []
        self.v0_x_red = None; self.v0_y_red = None; self.v0_z_red = None;
        self.v0_x_green = None; self.v0_y_green = None; self.v0_z_green = None;
        self.v0_x_blue = None; self.v0_y_blue = None; self.v0_z_blue = None;
        self.v0_x_yellow = None; self.v0_y_yellow = None; self.v0_z_yellow = None;
        self.v0_counter = 0
        self.v0_pts = deque(maxlen=self.args["buffer"])

        return


# OPENGL 3D PLOT WIDGET
class OL_3D_Plot(QtGui.QWidget):
    def __init__(self, parent=None):
        super(OL_3D_Plot, self).__init__(parent)

        layout = QtGui.QHBoxLayout()

        self.plot = gl.GLViewWidget()
        self.plot.opts['distance'] = 500
        self.plot.setWindowTitle('3-Dimensional Plot')

        # create the background grids
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)

        self.plot.addItem(gx)
        self.plot.addItem(gy)
        self.plot.addItem(gz)

        v0_xArray = []
        v0_yArray = []
        v0_zArray = []

        plot_xyz = np.vstack([v0_xArray, v0_yArray, v0_zArray]).transpose()

        self.trace_red = gl.GLLinePlotItem(pos=plot_xyz, color = pg.glColor(244, 66, 66), antialias = TRUE)
        self.trace_blue = gl.GLLinePlotItem(pos=plot_xyz, color=pg.glColor(66, 100, 244), antialias=TRUE)
        self.trace_green = gl.GLLinePlotItem(pos=plot_xyz, color=pg.glColor(66, 244, 104), antialias=TRUE)
        self.trace_yellow = gl.GLLinePlotItem(pos=plot_xyz, color=pg.glColor(244, 244, 66), antialias=TRUE)
        self.plot.addItem(self.trace_red)
        self.plot.addItem(self.trace_blue)
        self.plot.addItem(self.trace_green)
        self.plot.addItem(self.trace_yellow)
        layout.addWidget(self.plot)
        self.setLayout(layout)

