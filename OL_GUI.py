
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
        self.clear("all")

        # INITIALLY HIDE STOP/CLEAR
        self.button_stop.hide()
        self.button_clear.hide()

        # DEFINE BUTTON CLICK EVENTS
        self.button_start.clicked.connect(self.start_video)
        self.button_stop.clicked.connect(self.stop_video)
        self.button_clear.clicked.connect(lambda: self.clear("all"))

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
        self.video0.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.video0.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)

        # CREATE TIMER THREAD TO UPDATE FRAME EVERY (x) milliseconds
        self.timer = QTimer(self)
        #self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000.0 / 30.0)


    # GET VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def update_frame(self):
        print("----------------------------------------------------------------------------------------------")
        ret, self.v0_frame = self.video0.read()
        # ret, self.v1_frame = self.video1.read()
        # ret, self.v2_frame = self.video2.read()

        # VIDEO 0 OBJECT DETECTION returns data of given frame
        (self.v0_frame, self.v0_counter,
         self.v0_red_xyz_pts, self.v0_green_xyz_pts, self.v0_blue_xyz_pts, self.v0_yellow_xyz_pts,
         self.v0_isDetected) = \
        Object_Localization.Object_Localization(self.v0_frame,  self.v0_red_xyz_pts['pts'], self.v0_green_xyz_pts['pts'], self.v0_blue_xyz_pts['pts'], self.v0_yellow_xyz_pts['pts'], self.v0_counter)

        if(True in self.v0_isDetected.values()):


            if (self.v0_isDetected['red']):
                print("red pts: " + str(len(self.v0_red_xyz_pts['pts'])))
                if (len(self.v0_red_xyz_pts['pts']) > 10):
                    self.v0_red['x'].append(self.v0_red_xyz_pts['x'])
                    self.v0_red['y'].append(self.v0_red_xyz_pts['y'])
                    self.v0_red['z'].append(self.v0_red_xyz_pts['z'])
            else:
                self.clear("red")

            if (self.v0_isDetected['green']):
                print("green pts: " + str(len(self.v0_green_xyz_pts['pts'])))
                if (len(self.v0_green_xyz_pts['pts']) > 10):
                    self.v0_green['x'].append(self.v0_green_xyz_pts['x'])
                    self.v0_green['y'].append(self.v0_green_xyz_pts['y'])
                    self.v0_green['z'].append(self.v0_green_xyz_pts['z'])
            else:
                self.clear("green")

            if (self.v0_isDetected['blue']):
                print("blue pts: " + str(len(self.v0_blue_xyz_pts['pts'])))
                if (len(self.v0_blue_xyz_pts['pts']) > 10):
                    self.v0_blue['x'].append(self.v0_blue_xyz_pts['x'])
                    self.v0_blue['y'].append(self.v0_blue_xyz_pts['y'])
                    self.v0_blue['z'].append(self.v0_blue_xyz_pts['z'])
            else:
                self.clear("blue")

            if (self.v0_isDetected['yellow']):
                print("yellow pts: " + str(len(self.v0_yellow_xyz_pts['pts'])))
                if (len(self.v0_yellow_xyz_pts['pts']) > 10):
                    self.v0_yellow['x'].append(self.v0_yellow_xyz_pts['x'])
                    self.v0_yellow['y'].append(self.v0_yellow_xyz_pts['y'])
                    self.v0_yellow['z'].append(self.v0_yellow_xyz_pts['z'])
            else:
                self.clear("yellow")

        else:
            self.clear("all")

        # V0 PLOT MULTIPLE TRACES
        self.plot_v0.trace_red.setData(pos= np.vstack([self.v0_red['x'], self.v0_red['y'], self.v0_red['z']]).transpose())
        self.plot_v0.trace_green.setData(pos= np.vstack([self.v0_green['x'], self.v0_green['y'], self.v0_green['z']]).transpose())
        self.plot_v0.trace_blue.setData(pos= np.vstack([self.v0_blue['x'], self.v0_blue['y'], self.v0_blue['z']]).transpose())
        self.plot_v0.trace_yellow.setData(pos= np.vstack([self.v0_yellow['x'], self.v0_yellow['y'], self.v0_yellow['z']]).transpose())
        self.v0_frame = cv2.flip(self.v0_frame, 1)
        self.display_frame(self.v0_frame, 1)

    def display_frame(self, _frame, window=1):
        #qformat = QImage.Format_Indexed8
        qformat = QImage.Format_RGB888
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
            # self.label_video1.setPixmap(QPixmap.fromImage(outputImage))
            # self.label_video1.setScaledContents(True)
            # self.label_video2.setPixmap(QPixmap.fromImage(outputImage))
            # self.label_video2.setScaledContents(True)

        print("----------------------------------------------------------------------------------------------")

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
        self.clear("all")
        self.timer.stop()
        self.video0.release()

        # USED TO CLEAR VIDEO 0, VIDEO 1, VIDEO 2 DATA STRUCTURES
    def clear(self, mode):
        newDeque = deque(maxlen= self.args["buffer"])
        if(mode == "all"):
            print("clearing all");
            self.v0_red = {'x': [], 'y': [], 'z': []}
            self.v0_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            self.v0_green = {'x': [], 'y': [], 'z': []}
            self.v0_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            self.v0_blue = {'x': [], 'y': [], 'z': []}
            self.v0_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            self.v0_yellow = {'x': [], 'y': [], 'z': []}
            self.v0_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}
            self.v0_counter = 0

        elif(mode == "red"):
            print("clearing red");
            self.v0_red = {'x': [], 'y': [], 'z': []}
            self.v0_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

        elif (mode == "green"):
            print("clearing green");
            self.v0_green = {'x': [], 'y': [], 'z': []}
            self.v0_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

        elif (mode == "blue"):
            print("clearing blue");
            self.v0_blue = {'x': [], 'y': [], 'z': []}
            self.v0_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

        elif (mode == "yellow"):
            print("clearing yellow");
            self.v0_yellow = {'x': [], 'y': [], 'z': []}
            self.v0_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

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

