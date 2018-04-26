from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog, QWidget, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.uic.properties import QtWidgets, QtCore
from pyqtgraph.Qt import QtGui, QtCore
from collections import deque

import numpy as np
import Detection
import argparse
import cv2
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import matplotlib
import matplotlib.pyplot as plt


import Localization
MIN_NUM_POINTS = 10

class GUI_Detection(QDialog):
    def __init__(self):
        super(GUI_Detection, self).__init__()

        loadUi('GUI_Detection.ui', self)
        self.showMaximized()

        ap = argparse.ArgumentParser()
        ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
        self.args = vars(ap.parse_args())
        self.image = None


        # CLEAR DATA STRUCTURES
        self.clear("all", True, True, True)

        # INITIALLY HIDE STOP/CLEAR
        self.button_stop.hide()
        self.button_clear.hide()

        # DEFINE BUTTON CLICK EVENTS
        self.button_start.clicked.connect(self.start_video)
        self.button_stop.clicked.connect(self.stop_video)
        self.button_clear.clicked.connect(lambda: self.clear("all", True, True, True))

        # DEFINE CHECK BOX EVENTS
        self.checkBox_red.stateChanged.connect(self.red_state_changed)
        self.checkBox_green.stateChanged.connect(self.green_state_changed)
        self.checkBox_blue.stateChanged.connect(self.blue_state_changed)
        self.checkBox_yellow.stateChanged.connect(self.yellow_state_changed)

        # INITIALIZE CHECK BOX
        self.detect_red = False
        self.detect_green = False
        self.detect_blue = False
        self.detect_yellow = False
        self.checkBox_red.setChecked( self.detect_red)
        self.checkBox_green.setChecked( self.detect_green)
        self.checkBox_blue.setChecked( self.detect_blue)
        self.checkBox_yellow.setChecked( self.detect_yellow)

        # INITIALIZE 3D PLOT
        self.plot_v0 = OL_3D_Plot(self)
        self.plot_v1 = OL_3D_Plot(self)
        self.plot_v2 = OL_3D_Plot(self)
        # self.plot_v0 = VIDEO_3D_Plot(self)
        # self.plot_v1 = VIDEO_3D_Plot(self)
        # self.plot_v2 = VIDEO_3D_Plot(self)

        self.layout_plot.addWidget(self.plot_v0)
        self.layout_plot.addWidget(self.plot_v1)
        self.layout_plot.addWidget(self.plot_v2)

        # INITIAL VIDEO SOURCES (SUBJECT TO CHANGE BY USER)
        self.VIDEO_SOURCE_0 = "1"
        self.VIDEO_SOURCE_1 = "2"
        self.VIDEO_SOURCE_2 = "3"

        # COMBO BOXES
        comboBoxOptions = ["0", "1", "2", "3", "Video0.mp4", "Video1.mp4", "Video2.mp4"]
        self.comboBox_video0.addItems(comboBoxOptions)
        self.comboBox_video0.currentTextChanged.connect(self.comboBox_video0_changed)
        self.comboBox_video0.setCurrentIndex(comboBoxOptions.index("1"))

        self.comboBox_video1.currentTextChanged.connect(self.comboBox_video1_changed)
        self.comboBox_video1.addItems(comboBoxOptions)
        self.comboBox_video1.setCurrentIndex(comboBoxOptions.index("2"))

        self.comboBox_video2.currentTextChanged.connect(self.comboBox_video2_changed)
        self.comboBox_video2.addItems(comboBoxOptions)
        self.comboBox_video2.setCurrentIndex(comboBoxOptions.index("3"))

    def __del__(self):
        self.v0_frame = None
        self.v1_frame = None
        self.v2_frame = None
        self.stop_video()

    def closeEvent(self, event):
        print("closing")
        # here you can terminate your threads and do other stuff

        self.stop_video()
    def red_state_changed(self):
        if self.checkBox_red.isChecked():
            self.detect_red = True
        else:
            self.detect_red = False

    def green_state_changed(self):
        if self.checkBox_green.isChecked():
            self.detect_green = True
        else:
            self.detect_green = False

    def blue_state_changed(self):
        if self.checkBox_blue.isChecked():
            self.detect_blue = True
        else:
            self.detect_blue = False

    def yellow_state_changed(self):
        if self.checkBox_yellow.isChecked():
            self.detect_yellow = True
        else:
            self.detect_yellow = False

    def comboBox_video0_changed(self):
        try:
            self.VIDEO_SOURCE_0 = self.comboBox_video0.currentText()
            if(self.VIDEO_SOURCE_0 == '0' or self.VIDEO_SOURCE_0 == '1' or self.VIDEO_SOURCE_0 == '2' or self.VIDEO_SOURCE_0 == '3'):
                self.VIDEO_SOURCE_0 = int(self.VIDEO_SOURCE_0)
        except Exception as e:
            print(e)

    def comboBox_video1_changed(self):
        try:
            self.VIDEO_SOURCE_1 = self.comboBox_video1.currentText()
            if (self.VIDEO_SOURCE_1 == '0' or self.VIDEO_SOURCE_1 == '1' or self.VIDEO_SOURCE_1 == '2' or self.VIDEO_SOURCE_1 == '3'):
                self.VIDEO_SOURCE_1 = int(self.VIDEO_SOURCE_1)

        except Exception as e:
            print(e)

    def comboBox_video2_changed(self):
        try:
            self.VIDEO_SOURCE_2 = self.comboBox_video2.currentText()
            if (self.VIDEO_SOURCE_2 == '0' or self.VIDEO_SOURCE_2 == '1' or self.VIDEO_SOURCE_2 == '2' or self.VIDEO_SOURCE_2 == '3'):
                self.VIDEO_SOURCE_2 = int(self.VIDEO_SOURCE_2)
        except Exception as e:
            print(e)

    ## INITIALIZE VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def start_video(self):
        try:
            print("starting")
            # HIDE/SHOW GUI ELEMENTS
            self.button_start.hide()
            self.button_stop.show()
            self.button_clear.show()
            self.comboBox_video0.hide()
            self.comboBox_video1.hide()
            self.comboBox_video2.hide()
            self.video0 = cv2.VideoCapture(self.VIDEO_SOURCE_0)
            self.video0.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
            self.video0.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
            self.video1 = cv2.VideoCapture(self.VIDEO_SOURCE_1)
            self.video1.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
            self.video1.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
            self.video2 = cv2.VideoCapture(self.VIDEO_SOURCE_2)
            self.video2.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
            self.video2.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

            # CREATE TIMER THREAD TO UPDATE FRAME EVERY (x) milliseconds
            self.timer0 = QTimer(self)
            self.timer0.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer0.timeout.connect(self.update_frame0)
            self.timer0.start()

            self.timer1 = QTimer(self)
            self.timer1.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer1.timeout.connect(self.update_frame1)
            self.timer1.start()


            self.timer2 = QTimer(self)
            self.timer2.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer2.timeout.connect(self.update_frame2)
            self.timer2.start()

        except Exception as e:
            print(e)

    def update_frames(self):
        print("----------------------------------------------------------------------------------------------")
        if (not self.video0.isOpened() or not self.video1.isOpened() or not self.video2.isOpened()):
            print("stopping")
            self.stop_video()
            return
        ####################################################################################################
        #                                       VIDEO 0
        ####################################################################################################
        print("SOURCE 0")
        ret, self.v0_frame = self.video0.read()

        if ret == False:
            self.stop_video()
            return

        (self.v0_frame, self.v0_counter, self.v0_red_xyz_pts, self.v0_green_xyz_pts, self.v0_blue_xyz_pts,
         self.v0_yellow_xyz_pts, self.v0_isDetected) = Detection.Detection \
            (self.v0_frame, self.v0_counter,
             self.v0_red_xyz_pts['pts'], self.v0_green_xyz_pts['pts'], self.v0_blue_xyz_pts['pts'],
             self.v0_yellow_xyz_pts['pts'],
             self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow)

        if (True in self.v0_isDetected.values()):

            if (self.v0_isDetected['red']):
                print("red pts: " + str(len(self.v0_red_xyz_pts['pts'])))
                if (len(self.v0_red_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v0_red['x'].append(self.v0_red_xyz_pts['x'])
                    self.v0_red['y'].append(self.v0_red_xyz_pts['y'])
                    self.v0_red['z'].append(self.v0_red_xyz_pts['z'])
            else:
                self.clear("red", True, False, False)

            if (self.v0_isDetected['green']):
                print("green pts: " + str(len(self.v0_green_xyz_pts['pts'])))
                if (len(self.v0_green_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v0_green['x'].append(self.v0_green_xyz_pts['x'])
                    self.v0_green['y'].append(self.v0_green_xyz_pts['y'])
                    self.v0_green['z'].append(self.v0_green_xyz_pts['z'])
            else:
                self.clear("green", True, False, False)

            if (self.v0_isDetected['blue']):
                print("blue pts: " + str(len(self.v0_blue_xyz_pts['pts'])))
                if (len(self.v0_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v0_blue['x'].append(self.v0_blue_xyz_pts['x'])
                    self.v0_blue['y'].append(self.v0_blue_xyz_pts['y'])
                    self.v0_blue['z'].append(self.v0_blue_xyz_pts['z'])
            else:
                self.clear("blue", True, False, False)

            if (self.v0_isDetected['yellow']):
                print("yellow pts: " + str(len(self.v0_yellow_xyz_pts['pts'])))
                if (len(self.v0_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v0_yellow['x'].append(self.v0_yellow_xyz_pts['x'])
                    self.v0_yellow['y'].append(self.v0_yellow_xyz_pts['y'])
                    self.v0_yellow['z'].append(self.v0_yellow_xyz_pts['z'])
            else:
                self.clear("yellow", True, False, False)

        else:
            self.clear("all", True, False, False)

        # V0 PLOT MULTIPLE TRACES
        self.plot_v0.trace_red.setData(
            pos=np.vstack([self.v0_red['x'], self.v0_red['y'], self.v0_red['z']]).transpose())
        self.plot_v0.trace_green.setData(
            pos=np.vstack([self.v0_green['x'], self.v0_green['y'], self.v0_green['z']]).transpose())
        self.plot_v0.trace_blue.setData(
            pos=np.vstack([self.v0_blue['x'], self.v0_blue['y'], self.v0_blue['z']]).transpose())
        self.plot_v0.trace_yellow.setData(
            pos=np.vstack([self.v0_yellow['x'], self.v0_yellow['y'], self.v0_yellow['z']]).transpose())

        # print(self.v0_yellow['x'])
        # print(self.v0_yellow['y'])
        # print(self.v0_yellow['z'])
        # if (self.v0_red['x'][2]):

        # self.v0_frame = Localization.Localization(self.v0_red, self.v0_green, self.v0_blue, self.v0_yellow, self.v0_frame,
        #                             self.v1_red, self.v1_green, self.v1_blue, self.v1_yellow,
        #                             self.v2_red, self.v2_green, self.v2_blue, self.v2_yellow)

        self.display_frame(self.v0_frame, 0, 1)

        print("----------------------------------------------------------------------------------------------")
        if (not self.video0.isOpened() or not self.video1.isOpened() or not self.video2.isOpened()):
            print("stopping")
            self.stop_video()
            return
        ####################################################################################################
        #                                       VIDEO 1
        ####################################################################################################
        print("SOURCE 1")
        ret, self.v1_frame = self.video1.read()
        if ret == False:
            self.stop_video()
            return

        (self.v1_frame, self.v1_counter, self.v1_red_xyz_pts, self.v1_green_xyz_pts, self.v1_blue_xyz_pts,
         self.v1_yellow_xyz_pts, self.v1_isDetected) = Detection.Detection \
            (self.v1_frame, self.v1_counter,
             self.v1_red_xyz_pts['pts'], self.v1_green_xyz_pts['pts'], self.v1_blue_xyz_pts['pts'],
             self.v1_yellow_xyz_pts['pts'],
             self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow)

        if (True in self.v1_isDetected.values()):

            if (self.v1_isDetected['red']):
                print("red pts: " + str(len(self.v1_red_xyz_pts['pts'])))
                if (len(self.v1_red_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v1_red['x'].append(self.v1_red_xyz_pts['x'])
                    self.v1_red['y'].append(self.v1_red_xyz_pts['y'])
                    self.v1_red['z'].append(self.v1_red_xyz_pts['z'])
            else:
                self.clear("red", False, True, False)

            if (self.v1_isDetected['green']):
                print("green pts: " + str(len(self.v1_green_xyz_pts['pts'])))
                if (len(self.v1_green_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v1_green['x'].append(self.v1_green_xyz_pts['x'])
                    self.v1_green['y'].append(self.v1_green_xyz_pts['y'])
                    self.v1_green['z'].append(self.v1_green_xyz_pts['z'])
            else:
                self.clear("green", False, True, False)

            if (self.v1_isDetected['blue']):
                print("blue pts: " + str(len(self.v1_blue_xyz_pts['pts'])))
                if (len(self.v1_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v1_blue['x'].append(self.v1_blue_xyz_pts['x'])
                    self.v1_blue['y'].append(self.v1_blue_xyz_pts['y'])
                    self.v1_blue['z'].append(self.v1_blue_xyz_pts['z'])
            else:
                self.clear("blue", False, True, False)

            if (self.v1_isDetected['yellow']):
                print("yellow pts: " + str(len(self.v1_yellow_xyz_pts['pts'])))
                if (len(self.v1_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v1_yellow['x'].append(self.v1_yellow_xyz_pts['x'])
                    self.v1_yellow['y'].append(self.v1_yellow_xyz_pts['y'])
                    self.v1_yellow['z'].append(self.v1_yellow_xyz_pts['z'])
            else:
                self.clear("yellow", False, True, False)

        else:
            self.clear("all", False, True, False)

        # V1 PLOT MULTIPLE TRACES
        self.plot_v1.trace_red.setData(
            pos=np.vstack([self.v1_red['x'], self.v1_red['y'], self.v1_red['z']]).transpose())
        self.plot_v1.trace_green.setData(
            pos=np.vstack([self.v1_green['x'], self.v1_green['y'], self.v1_green['z']]).transpose())
        self.plot_v1.trace_blue.setData(
            pos=np.vstack([self.v1_blue['x'], self.v1_blue['y'], self.v1_blue['z']]).transpose())
        self.plot_v1.trace_yellow.setData(
            pos=np.vstack([self.v1_yellow['x'], self.v1_yellow['y'], self.v1_yellow['z']]).transpose())

        self.display_frame(self.v1_frame, 1, 1)

        print("----------------------------------------------------------------------------------------------")
        if (not self.video0.isOpened() or not self.video1.isOpened() or not self.video2.isOpened()):
            print("stopping")
            self.stop_video()
            return
        ####################################################################################################
        #                                       VIDEO 2
        ####################################################################################################

        print("SOURCE 2")
        ret, self.v2_frame = self.video2.read()
        if ret == False:
            self.stop_video()
            return

        (self.v2_frame, self.v2_counter, self.v2_red_xyz_pts, self.v2_green_xyz_pts, self.v2_blue_xyz_pts,
         self.v2_yellow_xyz_pts, self.v2_isDetected) = Detection.Detection \
            (self.v2_frame, self.v2_counter,
             self.v2_red_xyz_pts['pts'], self.v2_green_xyz_pts['pts'], self.v2_blue_xyz_pts['pts'],
             self.v2_yellow_xyz_pts['pts'],
             self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow)

        if (True in self.v2_isDetected.values()):

            if (self.v2_isDetected['red']):
                print("red pts: " + str(len(self.v2_red_xyz_pts['pts'])))
                if (len(self.v2_red_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v2_red['x'].append(self.v2_red_xyz_pts['x'])
                    self.v2_red['y'].append(self.v2_red_xyz_pts['y'])
                    self.v2_red['z'].append(self.v2_red_xyz_pts['z'])
            else:
                self.clear("red", False, False, True)

            if (self.v2_isDetected['green']):
                print("green pts: " + str(len(self.v2_green_xyz_pts['pts'])))
                if (len(self.v2_green_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v2_green['x'].append(self.v2_green_xyz_pts['x'])
                    self.v2_green['y'].append(self.v2_green_xyz_pts['y'])
                    self.v2_green['z'].append(self.v2_green_xyz_pts['z'])
            else:
                self.clear("green", False, False, True)

            if (self.v2_isDetected['blue']):
                print("blue pts: " + str(len(self.v2_blue_xyz_pts['pts'])))
                if (len(self.v2_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v2_blue['x'].append(self.v2_blue_xyz_pts['x'])
                    self.v2_blue['y'].append(self.v2_blue_xyz_pts['y'])
                    self.v2_blue['z'].append(self.v2_blue_xyz_pts['z'])
            else:
                self.clear("blue", False, False, True)

            if (self.v2_isDetected['yellow']):
                print("yellow pts: " + str(len(self.v2_yellow_xyz_pts['pts'])))
                if (len(self.v2_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
                    self.v2_yellow['x'].append(self.v2_yellow_xyz_pts['x'])
                    self.v2_yellow['y'].append(self.v2_yellow_xyz_pts['y'])
                    self.v2_yellow['z'].append(self.v2_yellow_xyz_pts['z'])
            else:
                self.clear("yellow", False, False, True)

        else:
            self.clear("all", False, False, True)

        # V2 PLOT MULTIPLE TRACES
        self.plot_v2.trace_red.setData(
            pos=np.vstack([self.v2_red['x'], self.v2_red['y'], self.v2_red['z']]).transpose())
        self.plot_v2.trace_green.setData(
            pos=np.vstack([self.v2_green['x'], self.v2_green['y'], self.v2_green['z']]).transpose())
        self.plot_v2.trace_blue.setData(
            pos=np.vstack([self.v2_blue['x'], self.v2_blue['y'], self.v2_blue['z']]).transpose())
        self.plot_v2.trace_yellow.setData(
            pos=np.vstack([self.v2_yellow['x'], self.v2_yellow['y'], self.v2_yellow['z']]).transpose())
        self.display_frame(self.v2_frame, 2, 1)
        #
        # self.v0_frame = cv2.flip(self.v0_frame, 1)
        # self.v1_frame = cv2.flip(self.v1_frame, 1)
        # self.v2_frame = cv2.flip(self.v2_frame, 1)

    def update_frame0(self):
        try:
            print("----------------------------------------------------------------------------------------------")
            if (not self.video0.isOpened() or not self.video1.isOpened() or not self.video2.isOpened()):
                print("stopping")
                self.v0_frame = None
                self.v1_frame = None
                self.v2_frame = None
                self.stop_video()
                return
            ####################################################################################################
            #                                       VIDEO 0
            ####################################################################################################
            print("SOURCE 0")
            ret, self.v0_frame = self.video0.read()

            if ret == False:
                self.stop_video()
                return


            (self.v0_frame, self.v0_counter, self.v0_red_xyz_pts, self.v0_green_xyz_pts, self.v0_blue_xyz_pts,
             self.v0_yellow_xyz_pts, self.v0_isDetected) = Detection.Detection \
                (self.v0_frame, self.v0_counter,
                 self.v0_red_xyz_pts['pts'], self.v0_green_xyz_pts['pts'], self.v0_blue_xyz_pts['pts'], self.v0_yellow_xyz_pts['pts'],
                 self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow)

            if (True in self.v0_isDetected.values()):

                if (self.v0_isDetected['red']):
                    print("red pts: " + str(len(self.v0_red_xyz_pts['pts'])))
                    if (len(self.v0_red_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v0_red['x'].append(self.v0_red_xyz_pts['x'])
                        self.v0_red['y'].append(self.v0_red_xyz_pts['y'])
                        self.v0_red['z'].append(self.v0_red_xyz_pts['z'])
                else:
                    self.clear("red", True, False, False)

                if (self.v0_isDetected['green']):
                    print("green pts: " + str(len(self.v0_green_xyz_pts['pts'])))
                    if (len(self.v0_green_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v0_green['x'].append(self.v0_green_xyz_pts['x'])
                        self.v0_green['y'].append(self.v0_green_xyz_pts['y'])
                        self.v0_green['z'].append(self.v0_green_xyz_pts['z'])
                else:
                    self.clear("green", True, False, False)

                if (self.v0_isDetected['blue']):
                    print("blue pts: " + str(len(self.v0_blue_xyz_pts['pts'])))
                    if (len(self.v0_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v0_blue['x'].append(self.v0_blue_xyz_pts['x'])
                        self.v0_blue['y'].append(self.v0_blue_xyz_pts['y'])
                        self.v0_blue['z'].append(self.v0_blue_xyz_pts['z'])
                else:
                    self.clear("blue", True, False, False)

                if (self.v0_isDetected['yellow']):
                    print("yellow pts: " + str(len(self.v0_yellow_xyz_pts['pts'])))
                    if (len(self.v0_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v0_yellow['x'].append(self.v0_yellow_xyz_pts['x'])
                        self.v0_yellow['y'].append(self.v0_yellow_xyz_pts['y'])
                        self.v0_yellow['z'].append(self.v0_yellow_xyz_pts['z'])
                else:
                    self.clear("yellow", True, False, False)

            else:
                self.clear("all", True, False, False)

            #V0 PLOT MULTIPLE TRACES
            self.plot_v0.trace_red.setData(pos=np.vstack([self.v0_red['x'], self.v0_red['y'], self.v0_red['z']]).transpose())
            self.plot_v0.trace_green.setData(pos=np.vstack([self.v0_green['x'], self.v0_green['y'], self.v0_green['z']]).transpose())
            self.plot_v0.trace_blue.setData(pos=np.vstack([self.v0_blue['x'], self.v0_blue['y'], self.v0_blue['z']]).transpose())
            self.plot_v0.trace_yellow.setData(pos=np.vstack([self.v0_yellow['x'], self.v0_yellow['y'], self.v0_yellow['z']]).transpose())

        except Exception as e:
            print(e)

    def update_frame1(self):

        try:
            print("----------------------------------------------------------------------------------------------")
            if (not self.video0.isOpened() or not self.video1.isOpened() or not self.video2.isOpened()):
                print("stopping")
                self.v0_frame = None
                self.v1_frame = None
                self.v2_frame = None
                self.stop_video()
                return
            ####################################################################################################
            #                                       VIDEO 1
            ####################################################################################################
            print("SOURCE 1")
            ret, self.v1_frame = self.video1.read()
            if ret == False:
                self.stop_video()
                return

            (self.v1_frame, self.v1_counter, self.v1_red_xyz_pts, self.v1_green_xyz_pts, self.v1_blue_xyz_pts,
             self.v1_yellow_xyz_pts, self.v1_isDetected) = Detection.Detection \
                (self.v1_frame, self.v1_counter,
                 self.v1_red_xyz_pts['pts'], self.v1_green_xyz_pts['pts'], self.v1_blue_xyz_pts['pts'], self.v1_yellow_xyz_pts['pts'],
                 self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow)

            if (True in self.v1_isDetected.values()):

                if (self.v1_isDetected['red']):
                    print("red pts: " + str(len(self.v1_red_xyz_pts['pts'])))
                    if (len(self.v1_red_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v1_red['x'].append(self.v1_red_xyz_pts['x'])
                        self.v1_red['y'].append(self.v1_red_xyz_pts['y'])
                        self.v1_red['z'].append(self.v1_red_xyz_pts['z'])
                else:
                    self.clear("red", False, True, False)

                if (self.v1_isDetected['green']):
                    print("green pts: " + str(len(self.v1_green_xyz_pts['pts'])))
                    if (len(self.v1_green_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v1_green['x'].append(self.v1_green_xyz_pts['x'])
                        self.v1_green['y'].append(self.v1_green_xyz_pts['y'])
                        self.v1_green['z'].append(self.v1_green_xyz_pts['z'])
                else:
                    self.clear("green", False, True, False)

                if (self.v1_isDetected['blue']):
                    print("blue pts: " + str(len(self.v1_blue_xyz_pts['pts'])))
                    if (len(self.v1_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v1_blue['x'].append(self.v1_blue_xyz_pts['x'])
                        self.v1_blue['y'].append(self.v1_blue_xyz_pts['y'])
                        self.v1_blue['z'].append(self.v1_blue_xyz_pts['z'])
                else:
                    self.clear("blue", False, True, False)

                if (self.v1_isDetected['yellow']):
                    print("yellow pts: " + str(len(self.v1_yellow_xyz_pts['pts'])))
                    if (len(self.v1_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v1_yellow['x'].append(self.v1_yellow_xyz_pts['x'])
                        self.v1_yellow['y'].append(self.v1_yellow_xyz_pts['y'])
                        self.v1_yellow['z'].append(self.v1_yellow_xyz_pts['z'])
                else:
                    self.clear("yellow", False, True, False)

            else:
                self.clear("all", False, True, False)

            # V1 PLOT MULTIPLE TRACES
            self.plot_v1.trace_red.setData(pos=np.vstack([self.v1_red['x'], self.v1_red['y'], self.v1_red['z']]).transpose())
            self.plot_v1.trace_green.setData(pos=np.vstack([self.v1_green['x'], self.v1_green['y'], self.v1_green['z']]).transpose())
            self.plot_v1.trace_blue.setData(pos=np.vstack([self.v1_blue['x'], self.v1_blue['y'], self.v1_blue['z']]).transpose())
            self.plot_v1.trace_yellow.setData(pos=np.vstack([self.v1_yellow['x'], self.v1_yellow['y'], self.v1_yellow['z']]).transpose())
            #self.display_frame(self.v1_frame, 1, 1)

        except Exception as e:
            print(e)

    def update_frame2(self):

        try:
            print("----------------------------------------------------------------------------------------------")
            if (not self.video0.isOpened() or not self.video1.isOpened() or not self.video2.isOpened()):
                print("stopping")
                self.v0_frame = None
                self.v1_frame = None
                self.v2_frame = None
                self.stop_video()
                return
            ####################################################################################################
            #                                       VIDEO 2
            ####################################################################################################

            print("SOURCE 2")
            ret, self.v2_frame = self.video2.read()
            if ret == False:
                self.stop_video()
                return

            (self.v2_frame, self.v2_counter, self.v2_red_xyz_pts, self.v2_green_xyz_pts, self.v2_blue_xyz_pts,
             self.v2_yellow_xyz_pts, self.v2_isDetected) = Detection.Detection \
                (self.v2_frame, self.v2_counter,
                 self.v2_red_xyz_pts['pts'], self.v2_green_xyz_pts['pts'], self.v2_blue_xyz_pts['pts'], self.v2_yellow_xyz_pts['pts'],
                 self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow)

            if (True in self.v2_isDetected.values()):

                if (self.v2_isDetected['red']):
                    print("red pts: " + str(len(self.v2_red_xyz_pts['pts'])))
                    if (len(self.v2_red_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v2_red['x'].append(self.v2_red_xyz_pts['x'])
                        self.v2_red['y'].append(self.v2_red_xyz_pts['y'])
                        self.v2_red['z'].append(self.v2_red_xyz_pts['z'])
                else:
                    self.clear("red", False, False, True)

                if (self.v2_isDetected['green']):
                    print("green pts: " + str(len(self.v2_green_xyz_pts['pts'])))
                    if (len(self.v2_green_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v2_green['x'].append(self.v2_green_xyz_pts['x'])
                        self.v2_green['y'].append(self.v2_green_xyz_pts['y'])
                        self.v2_green['z'].append(self.v2_green_xyz_pts['z'])
                else:
                    self.clear("green", False, False, True)

                if (self.v2_isDetected['blue']):
                    print("blue pts: " + str(len(self.v2_blue_xyz_pts['pts'])))
                    if (len(self.v2_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v2_blue['x'].append(self.v2_blue_xyz_pts['x'])
                        self.v2_blue['y'].append(self.v2_blue_xyz_pts['y'])
                        self.v2_blue['z'].append(self.v2_blue_xyz_pts['z'])
                else:
                    self.clear("blue", False, False, True)

                if (self.v2_isDetected['yellow']):
                    print("yellow pts: " + str(len(self.v2_yellow_xyz_pts['pts'])))
                    if (len(self.v2_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.v2_yellow['x'].append(self.v2_yellow_xyz_pts['x'])
                        self.v2_yellow['y'].append(self.v2_yellow_xyz_pts['y'])
                        self.v2_yellow['z'].append(self.v2_yellow_xyz_pts['z'])
                else:
                    self.clear("yellow", False, False, True)

            else:
                self.clear("all", False, False, True)


            # V2 PLOT MULTIPLE TRACES
            self.plot_v2.trace_red.setData(pos=np.vstack([self.v2_red['x'], self.v2_red['y'], self.v2_red['z']]).transpose())
            self.plot_v2.trace_green.setData(pos=np.vstack([self.v2_green['x'], self.v2_green['y'], self.v2_green['z']]).transpose())
            self.plot_v2.trace_blue.setData(pos=np.vstack([self.v2_blue['x'], self.v2_blue['y'], self.v2_blue['z']]).transpose())
            self.plot_v2.trace_yellow.setData(pos=np.vstack([self.v2_yellow['x'], self.v2_yellow['y'], self.v2_yellow['z']]).transpose())


            self.v0_frame, self.v1_frame, self.v2_frame = Localization.Localization(self.v0_frame, self.v1_frame, self.v2_frame,
                                        self.v0_blue, self.v0_yellow,self.v0_red,self.v0_green,  self.v0_isDetected,
                                        self.v1_blue, self.v1_yellow, self.v1_red, self.v1_green, self.v1_isDetected,
                                        self.v2_blue,self.v2_yellow,self.v2_red,self.v2_green,  self.v2_isDetected)

            self.display_frame(self.v0_frame, 0, 1)
            self.display_frame(self.v1_frame, 1, 1)
            self.display_frame(self.v2_frame, 2, 1)


        except Exception as e:
            print(e)


    def display_frame(self, _frame, source, window=1):

        try:
            print("displaying " + str(source))

            #_frame = cv2.flip(_frame, 1)


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
                if source == 0:
                    self.label_video0.setPixmap(QPixmap.fromImage(outputImage))
                    self.label_video0.setScaledContents(True)
                elif source == 1:
                    self.label_video1.setPixmap(QPixmap.fromImage(outputImage))
                    self.label_video1.setScaledContents(True)
                elif source == 2:
                    self.label_video2.setPixmap(QPixmap.fromImage(outputImage))
                    self.label_video2.setScaledContents(True)

            print("----------------------------------------------------------------------------------------------")

        except Exception as e:
            print(e)

    def stop_video(self):
        try:

            self.video0.release()
            self.timer0.stop()

            self.video1.release()
            self.timer1.stop()
            self.video2.release()
            self.timer2.stop()

            # HIDE/SHOW GUI ELEMENTS
            self.button_start.show()
            self.button_stop.hide()
            self.button_clear.hide()
            self.comboBox_video0.show()
            self.comboBox_video1.show()
            self.comboBox_video2.show()

            self.clear("all", True, True, True)

        except Exception as e:
            print(e)

        # USED TO CLEAR VIDEO 0, VIDEO 1, VIDEO 2 DATA STRUCTURES
    def clear(self, mode, source0, source1, source2):

        try:
            newDeque = deque(maxlen= self.args["buffer"])
            if(mode == "all"):
                print("clearing all");
                if(source0):
                    #(" clearing all source0");
                    self.v0_red = {'x': [], 'y': [], 'z': []}
                    self.v0_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v0_green = {'x': [], 'y': [], 'z': []}
                    self.v0_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v0_blue = {'x': [], 'y': [], 'z': []}
                    self.v0_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v0_yellow = {'x': [], 'y': [], 'z': []}
                    self.v0_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}
                    self.v0_counter = 0

                if (source1):
                    #print(" clearing all source1");
                    self.v1_red = {'x': [], 'y': [], 'z': []}
                    self.v1_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v1_green = {'x': [], 'y': [], 'z': []}
                    self.v1_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v1_blue = {'x': [], 'y': [], 'z': []}
                    self.v1_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v1_yellow = {'x': [], 'y': [], 'z': []}
                    self.v1_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}
                    self.v1_counter = 0

                if (source2):
                    #print(" clearing all source2");
                    self.v2_red = {'x': [], 'y': [], 'z': []}
                    self.v2_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v2_green = {'x': [], 'y': [], 'z': []}
                    self.v2_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v2_blue = {'x': [], 'y': [], 'z': []}
                    self.v2_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                    self.v2_yellow = {'x': [], 'y': [], 'z': []}
                    self.v2_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}
                    self.v2_counter = 0

            elif(mode == "red"):
                #print("clearing red");
                if (source0):
                    #print(" clearing red source0");
                    self.v0_red = {'x': [], 'y': [], 'z': []}
                    self.v0_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source1):
                    #print(" clearing red source1");
                    self.v1_red = {'x': [], 'y': [], 'z': []}
                    self.v1_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source2):
                    #print(" clearing red source2");
                    self.v2_red = {'x': [], 'y': [], 'z': []}
                    self.v2_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            elif (mode == "green"):
                #print("clearing green");
                if (source0):
                    #print(" clearing green source0");
                    self.v0_green = {'x': [], 'y': [], 'z': []}
                    self.v0_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source1):
                    #print(" clearing green source1");
                    self.v1_green = {'x': [], 'y': [], 'z': []}
                    self.v1_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source2):
                    #print(" clearing green source2");
                    self.v2_green = {'x': [], 'y': [], 'z': []}
                    self.v2_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            elif (mode == "blue"):
                #print("clearing blue");
                if (source0):
                    #print(" clearing blue source0");
                    self.v0_blue = {'x': [], 'y': [], 'z': []}
                    self.v0_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source1):
                    #print(" clearing blue source1");
                    self.v1_blue = {'x': [], 'y': [], 'z': []}
                    self.v1_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source2):
                    #print(" clearing blue source2");
                    self.v2_blue = {'x': [], 'y': [], 'z': []}
                    self.v2_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            elif (mode == "yellow"):
                #print("clearing yellow");
                if (source0):
                    #print(" clearing yellow source0");
                    self.v0_yellow = {'x': [], 'y': [], 'z': []}
                    self.v0_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source1):
                    #print(" clearing yellow source1");
                    self.v1_yellow = {'x': [], 'y': [], 'z': []}
                    self.v1_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

                if (source2):
                    #print(" clearing yellow source2");
                    self.v2_yellow = {'x': [], 'y': [], 'z': []}
                    self.v2_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            return

        except Exception as e:
            print(e)
        #print(" exiting clearing");


class VIDEO_3D_Plot(QtGui.QWidget):
    def __init__(self, parent=None):
        super(VIDEO_3D_Plot, self).__init__(parent)
        layout = QtGui.QHBoxLayout()
        self.plot = pg.PlotWidget()
        self.plot.setBackground('w')
        self.ax = plt.axes()
        v0_xArray = []
        v0_yArray = []

        #plot_xyz = np.vstack([v0_xArray, v0_yArray, v0_zArray]).transpose()


        self.trace_red = self.ax.plot(v0_xArray,v0_yArray)
        self.trace_blue = self.ax.plot(v0_xArray,v0_yArray)
        self.trace_green = self.ax.plot(v0_xArray,v0_yArray)
        self.trace_yellow = self.ax.plot(v0_xArray,v0_yArray)
        self.plot.addItem(self.trace_red)
        self.plot.addItem(self.trace_blue)
        self.plot.addItem(self.trace_green)
        self.plot.addItem(self.trace_yellow)
        layout.addWidget(self.plot)
        self.setLayout(layout)


# OPENGL 3D PLOT WIDGET
class OL_3D_Plot(QtGui.QWidget):
    def __init__(self, parent=None):
        super(OL_3D_Plot, self).__init__(parent)

        layout = QtGui.QHBoxLayout()

        self.plot = gl.GLViewWidget()
        self.plot.opts['distance'] = 1500
        self.plot.setWindowTitle('3-Dimensional Plot')
        # create the background grids
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        #gx.translate(-10, 0, 0)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        #gy.translate(0, -10, 0)
        gz = gl.GLGridItem()
        #gz.translate(0, 0, -10)
        gx.scale(50, 50, 50)
        gy.scale(50, 50, 50)
        gz.scale(50, 50, 50)
        self.plot.addItem(gx)
        self.plot.addItem(gy)
        self.plot.addItem(gz)

        v0_xArray = []
        v0_yArray = []
        v0_zArray = []

        plot_xyz = np.vstack([v0_xArray, v0_yArray, v0_zArray]).transpose()

        self.trace_red = gl.GLLinePlotItem(pos=plot_xyz, color = pg.glColor(244, 66, 66), antialias = True)
        self.trace_blue = gl.GLLinePlotItem(pos=plot_xyz, color=pg.glColor(66, 100, 244), antialias= True)
        self.trace_green = gl.GLLinePlotItem(pos=plot_xyz, color=pg.glColor(66, 244, 104), antialias= True)
        self.trace_yellow = gl.GLLinePlotItem(pos=plot_xyz, color=pg.glColor(244, 244, 66), antialias= True)
        self.plot.addItem(self.trace_red)
        self.plot.addItem(self.trace_blue)
        self.plot.addItem(self.trace_green)
        self.plot.addItem(self.trace_yellow)
        layout.addWidget(self.plot)
        self.setLayout(layout)

