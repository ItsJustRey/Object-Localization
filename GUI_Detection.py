from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog, QWidget, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.uic.properties import QtWidgets, QtCore
from pyqtgraph.Qt import QtGui, QtCore
from collections import deque

import sys, os
import numpy as np
import Detection
import argparse
import cv2
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import matplotlib
import matplotlib.pyplot as plt

from Video import Video
from OL_3D_Plot import OL_3D_Plot
import Localization
MIN_NUM_POINTS = 10


class GUI_Detection(QDialog):
    def __init__(self):
        super(GUI_Detection, self).__init__()

        # LOAD UI FROM .UI FILE (FROM QT DESIGNER)
        loadUi('GUI_Detection.ui', self)
        self.showMaximized()

        # INITIALIZE VIDEO OBJECTS
        self.v0 = Video("0")
        self.v1 = Video("1")
        self.v2 = Video("2")

        # CLEAR ALL DATA STRUCTURES
        self.clear(None, "all", True)

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

        # 3D PLOT FOR LOCALIZATION DATA
        self.plot_global = OL_3D_Plot(self)

        # ADD PLOTS TO UI LAYOUT BOXES
        self.layout_plot.addWidget(self.v0.plot)
        self.layout_plot.addWidget(self.v1.plot)
        self.layout_plot.addWidget(self.v2.plot)
        self.layout_global.addWidget(self.plot_global)

        # INITIAL VIDEO SOURCES (SUBJECT TO CHANGE BY USER)
        self.VIDEO_SOURCE_0 = 0
        self.VIDEO_SOURCE_1 = 0
        self.VIDEO_SOURCE_2 = 0

        # COMBO BOX OPTIONS
        comboBoxOptions = ["0", "1", "2", "3", "Video0.mp4", "Video1.mp4", "Video2.mp4"]
        self.comboBox_video0.addItems(comboBoxOptions)
        self.comboBox_video0.currentTextChanged.connect(self.comboBox_video0_changed)
        self.comboBox_video0.setCurrentIndex(comboBoxOptions.index("0"))

        self.comboBox_video1.currentTextChanged.connect(self.comboBox_video1_changed)
        self.comboBox_video1.addItems(comboBoxOptions)
        self.comboBox_video1.setCurrentIndex(comboBoxOptions.index("0"))

        self.comboBox_video2.currentTextChanged.connect(self.comboBox_video2_changed)
        self.comboBox_video2.addItems(comboBoxOptions)
        self.comboBox_video2.setCurrentIndex(comboBoxOptions.index("0"))

    def __del__(self):
        print("self destruct")
        self.stop_video()

    def closeEvent(self, event):
        print("closing")
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

    # START VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def start_video(self):
        try:
            # HIDE/SHOW GUI ELEMENTS
            self.button_start.hide()
            self.button_stop.show()
            self.button_clear.show()
            self.comboBox_video0.hide()
            self.comboBox_video1.hide()
            self.comboBox_video2.hide()

            # SET VIDEO SOURCES
            print("Starting!")
            self.v0.setVidSource(self.VIDEO_SOURCE_0)
            self.v1.setVidSource(self.VIDEO_SOURCE_1)
            self.v2.setVidSource(self.VIDEO_SOURCE_2)

            # CREATE TIMER THREADS TO UPDATE FRAME EVERY (x) milliseconds
            self.timer0 = QTimer(self)
            self.timer0.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer0.timeout.connect(lambda: self.update_frame(self.v0))
            self.timer0.start()

            self.timer1 = QTimer(self)
            self.timer1.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer1.timeout.connect(lambda: self.update_frame(self.v1))
            self.timer1.start()

            self.timer2 = QTimer(self)
            self.timer2.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer2.timeout.connect(lambda: self.update_frame(self.v2))
            self.timer2.start()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    ####################################################################################################
    #                                      update_frame(Video)
    ####################################################################################################
    def update_frame(self, video):
        try:
            if (not self.v0.vidCap.isOpened() or not self.v1.vidCap.isOpened() or not self.v2.vidCap.isOpened()):
                print("update_frame ... not opened")
                self.stop_video()
                return

            print("update_frame ... v" + video.id + " reading... ")
            self.global_inches = 0
            ret, video.frame = video.vidCap.read()

            if ret == False:
                print("update_frame ... v" + video.id + " opened, but can't be read")
                self.stop_video()
                return

            print("update_frame ... v" + video.id + " opened and read")

            # RETURN: new frame (opencv), new counter (int), each color points (xyz and deque),
            # isDetected (boolean dictionary), and global_inches (int)
            (video.frame, video.counter,
             video.red_xyz_pts, video.green_xyz_pts, video.blue_xyz_pts, video.yellow_xyz_pts,
             video.isDetected, self.global_inches) = \
            Detection.Detection \
            (video.frame, video.counter,
             video.red_xyz_pts['pts'], video.green_xyz_pts['pts'],
             video.blue_xyz_pts['pts'], video.yellow_xyz_pts['pts'],
             self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow, self.global_inches)
            # PASS in: current frame (opencv), current counter (int), each color points (deque),
            # detect_color (boolean from user selected checkbox), and global_inches (int)
            print("update_frame ... v" + video.id + " after detection")

            # CHECK IF A COLOR WAS DETECTED
            if (True in video.isDetected.values()):

                if (video.isDetected['red']):
                    if (len(video.red_xyz_pts['pts']) > MIN_NUM_POINTS):
                        video.red['x'].append(video.red_xyz_pts['x'])
                        video.red['y'].append(video.red_xyz_pts['y'])
                        video.red['z'].append(video.red_xyz_pts['z'])
                else:
                    # CLEAR RED FOR JUST THIS VIDEO
                    self.clear(video, "red", False)

                if (video.isDetected['green']):
                    if (len(video.green_xyz_pts['pts']) > MIN_NUM_POINTS):
                        self.video.green['x'].append(video.green_xyz_pts['x'])
                        self.video.green['y'].append(video.green_xyz_pts['y'])
                        self.video.green['z'].append(video.green_xyz_pts['z'])
                else:
                    # CLEAR GREEN FOR JUST THIS VIDEO
                    self.clear(video, "green", False)

                if (video.isDetected['blue']):
                    if (len(video.blue_xyz_pts['pts']) > MIN_NUM_POINTS):
                        video.blue['x'].append(video.blue_xyz_pts['x'])
                        video.blue['y'].append(video.blue_xyz_pts['y'])
                        video.blue['z'].append(video.blue_xyz_pts['z'])
                else:
                    # CLEAR BLUE FOR JUST THIS VIDEO
                    self.clear(video, "blue", False)

                if (video.isDetected['yellow']):

                    print("DETECTED YELLOW ... v" + video.id)
                    if (len(video.yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
                        video.yellow['x'].append(video.yellow_xyz_pts['x'])
                        video.yellow['y'].append(video.yellow_xyz_pts['y'])
                        video.yellow['z'].append(video.yellow_xyz_pts['z'])
                else:
                    # CLEAR YELLOW FOR JUST THIS VIDEO
                    self.clear(video, "yellow", False)

            else:
                # CLEAR ALL COLORS FOR JUST THIS VIDEO
                self.clear(None, "all", False)

            # UPDATE PLOTS
            self.update_plot(video)
            print("update_frame ... v" + video.id + "finished updating plot")
            # DISPLAY FRAMES
            self.display_frame(video.frame, int(video.id), 1)
            print("update_frame ... v" + video.id + "finished displaying frame")

        except Exception as e:
            print(e)

    # ####################################################################################################
    # #                                       VIDEO 0
    # ####################################################################################################
    # def update_frame0(self):
    #     try:
    #         if (not self.v0.vidCap.isOpened() or not self.v1.vidCap.isOpened() or not self.v2.vidCap.isOpened()):
    #             self.v0.frame = None
    #             self.v1.frame = None
    #             self.v2.frame = None
    #             self.stop_video()
    #             return
    #
    #
    #         self.global_points=0
    #         ret, self.v0.frame = self.v0.vidCap.read()
    #
    #
    #         if ret == False:
    #             self.stop_video()
    #             return
    #
    #
    #         (self.v0_frame, self.v0_counter, self.v0_red_xyz_pts, self.v0_green_xyz_pts, self.v0_blue_xyz_pts,
    #          self.v0_yellow_xyz_pts, self.v0_isDetected, self.global_inches) = Detection.Detection \
    #             (self.v0_frame, self.v0_counter,
    #              self.v0_red_xyz_pts['pts'], self.v0_green_xyz_pts['pts'], self.v0_blue_xyz_pts['pts'], self.v0_yellow_xyz_pts['pts'],
    #              self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow, self.global_inches)
    #
    #         if (True in self.v0_isDetected.values()):
    #
    #             if (self.v0_isDetected['red']):
    #                 if (len(self.v0_red_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v0_red['x'].append(self.v0_red_xyz_pts['x'])
    #                     self.v0_red['y'].append(self.v0_red_xyz_pts['y'])
    #                     self.v0_red['z'].append(self.v0_red_xyz_pts['z'])
    #             else:
    #                 self.clear("red", True, False, False)
    #
    #             if (self.v0_isDetected['green']):
    #                 if (len(self.v0_green_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v0_green['x'].append(self.v0_green_xyz_pts['x'])
    #                     self.v0_green['y'].append(self.v0_green_xyz_pts['y'])
    #                     self.v0_green['z'].append(self.v0_green_xyz_pts['z'])
    #             else:
    #                 self.clear("green", True, False, False)
    #
    #             if (self.v0_isDetected['blue']):
    #                 if (len(self.v0_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v0_blue['x'].append(self.v0_blue_xyz_pts['x'])
    #                     self.v0_blue['y'].append(self.v0_blue_xyz_pts['y'])
    #                     self.v0_blue['z'].append(self.v0_blue_xyz_pts['z'])
    #             else:
    #                 self.clear("blue", True, False, False)
    #
    #             if (self.v0_isDetected['yellow']):
    #                 if (len(self.v0_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v0_yellow['x'].append(self.v0_yellow_xyz_pts['x'])
    #                     self.v0_yellow['y'].append(self.v0_yellow_xyz_pts['y'])
    #                     self.v0_yellow['z'].append(self.v0_yellow_xyz_pts['z'])
    #             else:
    #                 self.clear("yellow", True, False, False)
    #
    #         else:
    #             self.clear("all", True, False, False)
    #
    #         #V0 PLOT MULTIPLE TRACES
    #         #self.plot_v0.trace_red.setData(pos=np.vstack([self.v0_red['x'], self.v0_red['y'], self.v0_red['z']]).transpose())
    #         #self.plot_v0.trace_green.setData(pos=np.vstack([self.v0_green['x'], self.v0_green['y'], self.v0_green['z']]).transpose())
    #         #self.plot_v0.trace_blue.setData(pos=np.vstack([self.v0_blue['x'], self.v0_blue['y'], self.v0_blue['z']]).transpose())
    #         #self.plot_v0.trace_yellow.setData(pos=np.vstack([self.v0_yellow['x'], self.v0_yellow['y'], self.v0_yellow['z']]).transpose())
    #
    #     except Exception as e:
    #         print(e)
    #
    # ####################################################################################################
    # #                                       VIDEO 1
    # ####################################################################################################
    # def update_frame1(self):
    #
    #     try:
    #         if (not self.v0.vidCap.isOpened() or not self.v1.vidCap.isOpened() or not self.v2.vidCap.isOpened()):
    #             self.v0_frame = None
    #             self.v1_frame = None
    #             self.v2_frame = None
    #             self.stop_video()
    #             return
    #
    #         self.global_points=0
    #         ret, self.v1_frame = self.v1.vidCap.read()
    #         if ret == False:
    #             self.stop_video()
    #             return
    #
    #         (self.v1_frame, self.v1_counter, self.v1_red_xyz_pts, self.v1_green_xyz_pts, self.v1_blue_xyz_pts,
    #          self.v1_yellow_xyz_pts, self.v1_isDetected, self.global_inches) = Detection.Detection \
    #             (self.v1_frame, self.v1_counter,
    #              self.v1_red_xyz_pts['pts'], self.v1_green_xyz_pts['pts'], self.v1_blue_xyz_pts['pts'], self.v1_yellow_xyz_pts['pts'],
    #              self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow, self.global_inches)
    #
    #         if (True in self.v1_isDetected.values()):
    #
    #             if (self.v1_isDetected['red']):
    #                 if (len(self.v1_red_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v1_red['x'].append(self.v1_red_xyz_pts['x'])
    #                     self.v1_red['y'].append(self.v1_red_xyz_pts['y'])
    #                     self.v1_red['z'].append(self.v1_red_xyz_pts['z'])
    #             else:
    #                 self.clear("red", False, True, False)
    #
    #             if (self.v1_isDetected['green']):
    #                 if (len(self.v1_green_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v1_green['x'].append(self.v1_green_xyz_pts['x'])
    #                     self.v1_green['y'].append(self.v1_green_xyz_pts['y'])
    #                     self.v1_green['z'].append(self.v1_green_xyz_pts['z'])
    #             else:
    #                 self.clear("green", False, True, False)
    #
    #             if (self.v1_isDetected['blue']):
    #                 if (len(self.v1_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v1_blue['x'].append(self.v1_blue_xyz_pts['x'])
    #                     self.v1_blue['y'].append(self.v1_blue_xyz_pts['y'])
    #                     self.v1_blue['z'].append(self.v1_blue_xyz_pts['z'])
    #             else:
    #                 self.clear("blue", False, True, False)
    #
    #             if (self.v1_isDetected['yellow']):
    #                 if (len(self.v1_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v1_yellow['x'].append(self.v1_yellow_xyz_pts['x'])
    #                     self.v1_yellow['y'].append(self.v1_yellow_xyz_pts['y'])
    #                     self.v1_yellow['z'].append(self.v1_yellow_xyz_pts['z'])
    #             else:
    #                 self.clear("yellow", False, True, False)
    #
    #         else:
    #             self.clear("all", False, True, False)
    #
    #         # V1 PLOT MULTIPLE TRACES
    #         #self.plot_v1.trace_red.setData(pos=np.vstack([self.v1_red['x'], self.v1_red['y'], self.v1_red['z']]).transpose())
    #         #self.plot_v1.trace_green.setData(pos=np.vstack([self.v1_green['x'], self.v1_green['y'], self.v1_green['z']]).transpose())
    #         #self.plot_v1.trace_blue.setData(pos=np.vstack([self.v1_blue['y'], self.v1_blue['x'], self.v1_blue['z']]).transpose())
    #         #self.plot_v1.trace_yellow.setData(pos=np.vstack([self.v1_yellow['x'], self.v1_yellow['y'], self.v1_yellow['z']]).transpose())
    #         #self.display_frame(self.v1_frame, 1, 1)
    #
    #     except Exception as e:
    #         print(e)
    #
    # ####################################################################################################
    # #                                       VIDEO 2
    # ####################################################################################################
    # def update_frame2(self):
    #     try:
    #         if (not self.v0.vidCap.isOpened() or not self.v1.vidCap.isOpened() or not self.v2.vidCap.isOpened()):
    #             self.v0_frame = None
    #             self.v1_frame = None
    #             self.v2_frame = None
    #             self.stop_video()
    #             return
    #
    #         self.global_inches=0
    #         ret, self.v2_frame = self.v2.vidCap.read()
    #         if ret == False:
    #             self.stop_video()
    #             return
    #
    #         (self.v2_frame, self.v2_counter, self.v2_red_xyz_pts, self.v2_green_xyz_pts, self.v2_blue_xyz_pts,
    #          self.v2_yellow_xyz_pts, self.v2_isDetected, self.global_inches) = Detection.Detection \
    #             (self.v2_frame, self.v2_counter,
    #              self.v2_red_xyz_pts['pts'], self.v2_green_xyz_pts['pts'], self.v2_blue_xyz_pts['pts'], self.v2_yellow_xyz_pts['pts'],
    #              self.detect_red, self.detect_green, self.detect_blue, self.detect_yellow, self.global_inches)
    #
    #         if (True in self.v2_isDetected.values()):
    #
    #             if (self.v2_isDetected['red']):
    #                 if (len(self.v2_red_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v2_red['x'].append(self.v2_red_xyz_pts['x'])
    #                     self.v2_red['y'].append(self.v2_red_xyz_pts['y'])
    #                     self.v2_red['z'].append(self.v2_red_xyz_pts['z'])
    #             else:
    #                 self.clear("red", False, False, True)
    #
    #             if (self.v2_isDetected['green']):
    #                 if (len(self.v2_green_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v2_green['x'].append(self.v2_green_xyz_pts['x'])
    #                     self.v2_green['y'].append(self.v2_green_xyz_pts['y'])
    #                     self.v2_green['z'].append(self.v2_green_xyz_pts['z'])
    #             else:
    #                 self.clear("green", False, False, True)
    #
    #             if (self.v2_isDetected['blue']):
    #                 if (len(self.v2_blue_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v2_blue['x'].append(self.v2_blue_xyz_pts['x'])
    #                     self.v2_blue['y'].append(self.v2_blue_xyz_pts['y'])
    #                     self.v2_blue['z'].append(self.v2_blue_xyz_pts['z'])
    #             else:
    #                 self.clear("blue", False, False, True)
    #
    #             if (self.v2_isDetected['yellow']):
    #                 if (len(self.v2_yellow_xyz_pts['pts']) > MIN_NUM_POINTS):
    #                     self.v2_yellow['x'].append(self.v2_yellow_xyz_pts['x'])
    #                     self.v2_yellow['y'].append(self.v2_yellow_xyz_pts['y'])
    #                     self.v2_yellow['z'].append(self.v2_yellow_xyz_pts['z'])
    #             else:
    #                 self.clear("yellow", False, False, True)
    #
    #         else:
    #             self.clear("all", False, False, True)
    #
    #         # V2 PLOT MULTIPLE TRACES
    #         self.plot_v2.trace_red.setData(pos=np.vstack([self.v2_red['x'], self.v2_red['y'], self.v2_red['z']]).transpose())
    #         self.plot_v2.trace_green.setData(pos=np.vstack([self.v2_green['x'], self.v2_green['y'], self.v2_green['z']]).transpose())
    #         self.plot_v2.trace_blue.setData(pos=np.vstack([self.v2_blue['x'], self.v2_blue['y'], self.v2_blue['z']]).transpose())
    #         self.plot_v2.trace_yellow.setData(pos=np.vstack([self.v2_yellow['x'], self.v2_yellow['y'], self.v2_yellow['z']]).transpose())
    #
    #
    #         (self.v0_frame, self.v1_frame, self.v2_frame, self.global_red_xyz_pts, self.global_green_xyz_pts, self.global_blue_xyz_pts, self.global_yellow_xyz_pts) = \
    #             Localization.Localization(self.v0_frame, self.v1_frame, self.v2_frame,
    #                                       self.v0_blue, self.v0_yellow,self.v0_red,self.v0_green,  self.v0_isDetected,
    #                                       self.v1_blue, self.v1_yellow, self.v1_red, self.v1_green, self.v1_isDetected,
    #                                       self.v2_blue,self.v2_yellow,self.v2_red,self.v2_green,  self.v2_isDetected, self.global_inches)
    #
    #         if(self.global_red_xyz_pts['isCalculated'] is True):
    #             self.global_red['x'].append(self.global_red_xyz_pts['x'])
    #             self.global_red['y'].append(self.global_red_xyz_pts['y'])
    #             self.global_red['z'].append(self.global_red_xyz_pts['z'])
    #
    #         if(self.global_green_xyz_pts['isCalculated'] is True):
    #             self.global_green['x'].append(self.global_green_xyz_pts['x'])
    #             self.global_green['y'].append(self.global_green_xyz_pts['y'])
    #             self.global_green['z'].append(self.global_green_xyz_pts['z'])
    #
    #         if(self.global_blue_xyz_pts['isCalculated'] is True):
    #             self.global_blue['x'].append(self.global_blue_xyz_pts['x'])
    #             self.global_blue['y'].append(self.global_blue_xyz_pts['y'])
    #             self.global_blue['z'].append(self.global_blue_xyz_pts['z'])
    #
    #         if(self.global_yellow_xyz_pts['isCalculated'] is True):
    #             self.global_yellow['x'].append(self.global_yellow_xyz_pts['x'])
    #             self.global_yellow['y'].append(self.global_yellow_xyz_pts['y'])
    #             self.global_yellow['z'].append(self.global_yellow_xyz_pts['z'])
    #
    #
    #         self.plot_v0.trace_red.setData(pos=np.vstack([self.global_red['x'], self.global_red['y'], self.global_red['z']]).transpose())
    #         self.plot_v0.trace_green.setData(pos=np.vstack([self.global_green['x'], self.global_green['y'], self.global_green['z']]).transpose())
    #         self.plot_v0.trace_blue.setData(pos=np.vstack([self.global_blue['x'], self.global_blue['z'], self.global_blue['y']]).transpose())
    #         self.plot_v0.trace_yellow.setData(pos=np.vstack([self.global_yellow['x'], self.global_yellow['y'], self.global_yellow['z']]).transpose())
    #
    #
    #         self.plot_v1.trace_red.setData(pos=np.vstack([self.global_red['y'], self.global_red['x'], self.global_red['z']]).transpose())
    #         self.plot_v1.trace_green.setData(pos=np.vstack([self.global_green['y'], self.global_green['x'], self.global_green['z']]).transpose())
    #         self.plot_v1.trace_blue.setData(pos=np.vstack([self.global_blue['y'], self.global_blue['x'], self.global_blue['z']]).transpose())
    #         self.plot_v1.trace_yellow.setData(pos=np.vstack([self.global_yellow['y'], self.global_yellow['x'], self.global_yellow['z']]).transpose())
    #
    #         self.display_frame(self.v0_frame, 0, 1)
    #         self.display_frame(self.v1_frame, 1, 1)
    #         self.display_frame(self.v2_frame, 2, 1)
    #
    #     except Exception as e:
    #         print(e)


    def display_frame(self, _frame, source, window=1):
        try:
            print("displaying")
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


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def update_plot(self, video):

        video.plot.trace_red.setData(pos=np.vstack([video.red['x'], video.red['y'], video.red['z']]).transpose())
        video.plot.trace_green.setData(pos=np.vstack([video.green['x'], video.green['y'], video.green['z']]).transpose())
        video.plot.trace_blue.setData(pos=np.vstack([video.blue['x'], video.blue['y'], video.blue['z']]).transpose())
        video.plot.trace_yellow.setData(pos=np.vstack([video.yellow['x'], video.yellow['y'], video.yellow['z']]).transpose())

    def stop_video(self):
        try:
            print(" Stopping...")
            self.v0.vidCap.release()
            self.v0.frame = None
            self.timer0.stop()

            self.v1.vidCap.release()
            self.v1.frame = None
            self.timer1.stop()

            self.v2.vidCap.release()
            self.v2.frame = None
            self.timer2.stop()

            # HIDE/SHOW GUI ELEMENTS
            self.button_start.show()
            self.button_stop.hide()
            self.button_clear.hide()
            self.comboBox_video0.show()
            self.comboBox_video1.show()
            self.comboBox_video2.show()

            self.clear(None, "all", True)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    # USED TO CLEAR VIDEO 0, VIDEO 1, VIDEO 2 DATA STRUCTURES
    def clear(self, video, color, mode):

        print(" Clearing...")
        try:
            if(color == "all"):
                print(" Clearing All ...")
                self.global_red =    {'x': [], 'y': [], 'z': []}
                self.global_green =  {'x': [], 'y': [], 'z': []}
                self.global_blue =   {'x': [], 'y': [], 'z': []}
                self.global_yellow = {'x': [], 'y': [], 'z': []}

                self.global_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None,
                                           'length2': None, 'isCalculated': False}
                self.global_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None,
                                             'length2': None, 'isCalculated': False}
                self.global_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None,
                                            'length2': None, 'isCalculated': False}
                self.global_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None,
                                              'length2': None, 'isCalculated': False}
                # CLEAR ALL VIDEOS
                if(mode):
                    self.v0.clear(color)
                    self.v1.clear(color)
                    self.v2.clear(color)
                # CLEAR SPECIFIC VIDEO
                else:
                    video.clear(color)
            else:
                # CLEAR SPECIFIC COLOR
                video.clear(color)

            return

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

