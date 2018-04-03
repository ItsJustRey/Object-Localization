
import Object_Localization as Object_Localization

#
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog, QWidget, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
import argparse
import cv2
from PyQt5.uic.properties import QtWidgets, QtCore

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui, QtCore

import numpy as np
import Object_Localization
from collections import deque

class OL_GUI(QDialog):
    def __init__(self):
        super(OL_GUI, self).__init__()

        loadUi('GUI.ui', self)
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

        # SET UP 3D PLOT
        self.plot_v0 = OL_3D_Plot(self)
        self.plot_v1 = OL_3D_Plot(self)
        self.plot_v2 = OL_3D_Plot(self)
        self.layout_plot.addWidget(self.plot_v0)
        self.layout_plot.addWidget(self.plot_v1)
        self.layout_plot.addWidget(self.plot_v2)

        # INITIAL VIDEO SOURCES (SUBJECT TO CHANGE BY USER)
        # self.VIDEO_SOURCE_0 = "Video0.mp4"
        #
        # self.VIDEO_SOURCE_1 = "Video1.mp4"
        #
        # self.VIDEO_SOURCE_2 = "Video2.mp4"

        # COMBO BOXES
        comboBoxOptions = ["0", "1", "2", "Video0.mp4", "Video1.mp4", "Video2.mp4"]
        self.comboBox_video0.addItems(comboBoxOptions)
        self.comboBox_video0.currentTextChanged.connect(self.comboBox_video0_changed)
        self.comboBox_video0.setCurrentIndex(comboBoxOptions.index("Video0.mp4"))

        self.comboBox_video1.currentTextChanged.connect(self.comboBox_video1_changed)
        self.comboBox_video1.addItems(comboBoxOptions)
        self.comboBox_video1.setCurrentIndex(comboBoxOptions.index("Video1.mp4"))

        self.comboBox_video2.currentTextChanged.connect(self.comboBox_video2_changed)
        self.comboBox_video2.addItems(comboBoxOptions)
        self.comboBox_video2.setCurrentIndex(comboBoxOptions.index("Video2.mp4"))



    def comboBox_video0_changed(self):
        self.VIDEO_SOURCE_0 = self.comboBox_video0.currentText()
        if(self.VIDEO_SOURCE_0 == '0' or self.VIDEO_SOURCE_0 == '1' or self.VIDEO_SOURCE_0 == '2'):
            self.VIDEO_SOURCE_0 = int(self.VIDEO_SOURCE_0)

    def comboBox_video1_changed(self):
        self.VIDEO_SOURCE_1 = self.comboBox_video1.currentText()
        if (self.VIDEO_SOURCE_1 == '0' or self.VIDEO_SOURCE_1 == '1' or self.VIDEO_SOURCE_1 == '2'):
            self.VIDEO_SOURCE_1 = int(self.VIDEO_SOURCE_1)

    def comboBox_video2_changed(self):
        self.VIDEO_SOURCE_2 = self.comboBox_video2.currentText()
        if (self.VIDEO_SOURCE_2 == '0' or self.VIDEO_SOURCE_2 == '1' or self.VIDEO_SOURCE_2 == '2'):
            self.VIDEO_SOURCE_2 = int(self.VIDEO_SOURCE_2)

    # INITIALIZE VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def start_video(self):

        # HIDE/SHOW GUI ELEMENTS
        self.button_start.hide()
        self.button_stop.show()
        self.button_clear.show()
        self.comboBox_video0.hide()
        self.comboBox_video1.hide()
        self.comboBox_video2.hide()

        # INITIALIZE VIDEO 0 FRAMES AND DATA
        #self.video0 = cv2.VideoCapture(int(self.VIDEO_SOURCE_0))
        self.video0 = cv2.VideoCapture(self.VIDEO_SOURCE_0)
        self.video0.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.video0.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
        #self.fps_v0 = self.video0.get(cv2.CAP_PROP_FPS)

        # INITIALIZE VIDEO 1 FRAMES AND DATA
        #self.video1 = cv2.VideoCapture(int(self.VIDEO_SOURCE_1))
        self.video1 = cv2.VideoCapture(self.VIDEO_SOURCE_1)
        self.video1.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.video1.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

        # INITIALIZE VIDEO 2 FRAMES AND DATA
        self.video2 = cv2.VideoCapture(self.VIDEO_SOURCE_2)
        self.video2.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.video2.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

        # CREATE TIMER THREAD TO UPDATE FRAME EVERY (x) milliseconds
        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)



    # GET VIDEO 0, VIDEO 1, and VIDEO 2 FRAMES AND DATA
    def update_frame(self):
        if(not self.video0.isOpened() or not self.video1.isOpened() or not self.video2.isOpened()):
            self.stop_video()
            return

        print("----------------------------------------------------------------------------------------------")
        ####################################################################################################
        #                                       VIDEO 0
        ####################################################################################################
        ret, self.v0_frame = self.video0.read()
        if ret == False:
            self.stop_video()
            return

        (self.v0_frame, self.v0_counter, self.v0_red_xyz_pts, self.v0_green_xyz_pts, self.v0_blue_xyz_pts, self.v0_yellow_xyz_pts, self.v0_isDetected) = Object_Localization.Object_Localization \
            (self.v0_frame, self.v0_counter, self.v0_red_xyz_pts['pts'], self.v0_green_xyz_pts['pts'], self.v0_blue_xyz_pts['pts'], self.v0_yellow_xyz_pts['pts'])

        if(True in self.v0_isDetected.values()):

            if (self.v0_isDetected['red']):
                print("red pts: " + str(len(self.v0_red_xyz_pts['pts'])))
                if (len(self.v0_red_xyz_pts['pts']) > 10):
                    self.v0_red['x'].append(self.v0_red_xyz_pts['x'])
                    self.v0_red['y'].append(self.v0_red_xyz_pts['y'])
                    self.v0_red['z'].append(self.v0_red_xyz_pts['z'])
            else:
                self.clear("red", True, False, False)

            if (self.v0_isDetected['green']):
                print("green pts: " + str(len(self.v0_green_xyz_pts['pts'])))
                if (len(self.v0_green_xyz_pts['pts']) > 10):
                    self.v0_green['x'].append(self.v0_green_xyz_pts['x'])
                    self.v0_green['y'].append(self.v0_green_xyz_pts['y'])
                    self.v0_green['z'].append(self.v0_green_xyz_pts['z'])
            else:
                self.clear("green", True, False, False)

            if (self.v0_isDetected['blue']):
                print("blue pts: " + str(len(self.v0_blue_xyz_pts['pts'])))
                if (len(self.v0_blue_xyz_pts['pts']) > 10):
                    self.v0_blue['x'].append(self.v0_blue_xyz_pts['x'])
                    self.v0_blue['y'].append(self.v0_blue_xyz_pts['y'])
                    self.v0_blue['z'].append(self.v0_blue_xyz_pts['z'])
            else:
                self.clear("blue", True, False, False)

            if (self.v0_isDetected['yellow']):
                print("yellow pts: " + str(len(self.v0_yellow_xyz_pts['pts'])))
                if (len(self.v0_yellow_xyz_pts['pts']) > 10):
                    self.v0_yellow['x'].append(self.v0_yellow_xyz_pts['x'])
                    self.v0_yellow['y'].append(self.v0_yellow_xyz_pts['y'])
                    self.v0_yellow['z'].append(self.v0_yellow_xyz_pts['z'])
            else:
                self.clear("yellow", True, False, False)

        else:
            self.clear("all", True, False, False)

        ####################################################################################################
        #                                       VIDEO 1
        ####################################################################################################
        ret, self.v1_frame = self.video1.read()
        if ret == False:
            self.stop_video()
            return

        (self.v1_frame, self.v1_counter, self.v1_red_xyz_pts, self.v1_green_xyz_pts, self.v1_blue_xyz_pts, self.v1_yellow_xyz_pts, self.v1_isDetected) = Object_Localization.Object_Localization\
            (self.v1_frame, self.v1_counter, self.v1_red_xyz_pts['pts'],self.v1_green_xyz_pts['pts'], self.v1_blue_xyz_pts['pts'],self.v1_yellow_xyz_pts['pts'])

        if (True in self.v1_isDetected.values()):

            if (self.v1_isDetected['red']):
                print("red pts: " + str(len(self.v1_red_xyz_pts['pts'])))
                if (len(self.v1_red_xyz_pts['pts']) > 10):
                    self.v1_red['x'].append(self.v1_red_xyz_pts['x'])
                    self.v1_red['y'].append(self.v1_red_xyz_pts['y'])
                    self.v1_red['z'].append(self.v1_red_xyz_pts['z'])
            else:
                self.clear("red", False, True, False)

            if (self.v1_isDetected['green']):
                print("green pts: " + str(len(self.v1_green_xyz_pts['pts'])))
                if (len(self.v1_green_xyz_pts['pts']) > 10):
                    self.v1_green['x'].append(self.v1_green_xyz_pts['x'])
                    self.v1_green['y'].append(self.v1_green_xyz_pts['y'])
                    self.v1_green['z'].append(self.v1_green_xyz_pts['z'])
            else:
                self.clear("green", False, True, False)

            if (self.v1_isDetected['blue']):
                print("blue pts: " + str(len(self.v1_blue_xyz_pts['pts'])))
                if (len(self.v1_blue_xyz_pts['pts']) > 10):
                    self.v1_blue['x'].append(self.v1_blue_xyz_pts['x'])
                    self.v1_blue['y'].append(self.v1_blue_xyz_pts['y'])
                    self.v1_blue['z'].append(self.v1_blue_xyz_pts['z'])
            else:
                self.clear("blue", False, True, False)

            if (self.v1_isDetected['yellow']):
                print("yellow pts: " + str(len(self.v1_yellow_xyz_pts['pts'])))
                if (len(self.v1_yellow_xyz_pts['pts']) > 10):
                    self.v1_yellow['x'].append(self.v1_yellow_xyz_pts['x'])
                    self.v1_yellow['y'].append(self.v1_yellow_xyz_pts['y'])
                    self.v1_yellow['z'].append(self.v1_yellow_xyz_pts['z'])
            else:
                self.clear("yellow", False, True, False)

        else:
            self.clear("all", False, True, False)

        ####################################################################################################
        #                                       VIDEO 2
        ####################################################################################################

        ret, self.v2_frame = self.video2.read()
        if ret == False:
            self.stop_video()
            return


        (self.v2_frame, self.v2_counter, self.v2_red_xyz_pts, self.v2_green_xyz_pts, self.v2_blue_xyz_pts, self.v2_yellow_xyz_pts, self.v2_isDetected) = Object_Localization.Object_Localization \
            (self.v2_frame, self.v2_counter, self.v2_red_xyz_pts['pts'], self.v2_green_xyz_pts['pts'], self.v2_blue_xyz_pts['pts'], self.v2_yellow_xyz_pts['pts'])

        if (True in self.v2_isDetected.values()):

            if (self.v2_isDetected['red']):
                print("red pts: " + str(len(self.v2_red_xyz_pts['pts'])))
                if (len(self.v2_red_xyz_pts['pts']) > 10):
                    self.v2_red['x'].append(self.v2_red_xyz_pts['x'])
                    self.v2_red['y'].append(self.v2_red_xyz_pts['y'])
                    self.v2_red['z'].append(self.v2_red_xyz_pts['z'])
            else:
                self.clear("red", False, False, True)

            if (self.v2_isDetected['green']):
                print("green pts: " + str(len(self.v2_green_xyz_pts['pts'])))
                if (len(self.v2_green_xyz_pts['pts']) > 10):
                    self.v2_green['x'].append(self.v2_green_xyz_pts['x'])
                    self.v2_green['y'].append(self.v2_green_xyz_pts['y'])
                    self.v2_green['z'].append(self.v2_green_xyz_pts['z'])
            else:
                self.clear("green", False, False, True)

            if (self.v2_isDetected['blue']):
                print("blue pts: " + str(len(self.v2_blue_xyz_pts['pts'])))
                if (len(self.v2_blue_xyz_pts['pts']) > 10):
                    self.v2_blue['x'].append(self.v2_blue_xyz_pts['x'])
                    self.v2_blue['y'].append(self.v2_blue_xyz_pts['y'])
                    self.v2_blue['z'].append(self.v2_blue_xyz_pts['z'])
            else:
                self.clear("blue", False, False, True)

            if (self.v2_isDetected['yellow']):
                print("yellow pts: " + str(len(self.v2_yellow_xyz_pts['pts'])))
                if (len(self.v2_yellow_xyz_pts['pts']) > 10):
                    self.v2_yellow['x'].append(self.v2_yellow_xyz_pts['x'])
                    self.v2_yellow['y'].append(self.v2_yellow_xyz_pts['y'])
                    self.v2_yellow['z'].append(self.v2_yellow_xyz_pts['z'])
            else:
                self.clear("yellow", False, False, True)

        else:
            self.clear("all", False, False, True)

        # V0 PLOT MULTIPLE TRACES
        self.plot_v0.trace_red.setData(pos= np.vstack([self.v0_red['x'], self.v0_red['y'], self.v0_red['z']]).transpose())
        self.plot_v0.trace_green.setData(pos= np.vstack([self.v0_green['x'], self.v0_green['y'], self.v0_green['z']]).transpose())
        self.plot_v0.trace_blue.setData(pos= np.vstack([self.v0_blue['x'], self.v0_blue['y'], self.v0_blue['z']]).transpose())
        self.plot_v0.trace_yellow.setData(pos= np.vstack([self.v0_yellow['x'], self.v0_yellow['y'], self.v0_yellow['z']]).transpose())

        # V1 PLOT MULTIPLE TRACES
        self.plot_v1.trace_red.setData(pos=np.vstack([self.v1_red['x'], self.v1_red['y'], self.v1_red['z']]).transpose())
        self.plot_v1.trace_green.setData(pos=np.vstack([self.v1_green['x'], self.v1_green['y'], self.v1_green['z']]).transpose())
        self.plot_v1.trace_blue.setData(pos=np.vstack([self.v1_blue['x'], self.v1_blue['y'], self.v1_blue['z']]).transpose())
        self.plot_v1.trace_yellow.setData(pos=np.vstack([self.v1_yellow['x'], self.v1_yellow['y'], self.v1_yellow['z']]).transpose())

        # V0 PLOT MULTIPLE TRACES
        self.plot_v2.trace_red.setData(pos=np.vstack([self.v2_red['x'], self.v2_red['y'], self.v2_red['z']]).transpose())
        self.plot_v2.trace_green.setData(pos=np.vstack([self.v2_green['x'], self.v2_green['y'], self.v2_green['z']]).transpose())
        self.plot_v2.trace_blue.setData(pos=np.vstack([self.v2_blue['x'], self.v2_blue['y'], self.v2_blue['z']]).transpose())
        self.plot_v2.trace_yellow.setData(pos=np.vstack([self.v2_yellow['x'], self.v2_yellow['y'], self.v2_yellow['z']]).transpose())

        # self.v0_frame = cv2.flip(self.v0_frame, 1)
        # self.v1_frame = cv2.flip(self.v1_frame, 1)
        #self.v2_frame = cv2.flip(self.v2_frame, 1)
        self.display_frame(self.v0_frame, 0, 1)
        self.display_frame(self.v1_frame, 1, 1)
        self.display_frame(self.v2_frame, 2, 1)

    def display_frame(self, _frame, source, window=1):
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

    def stop_video(self):

        # HIDE/SHOW GUI ELEMENTS
        self.button_start.show()
        self.button_stop.hide()
        self.button_clear.hide()
        self.comboBox_video0.show()
        self.comboBox_video1.show()
        self.comboBox_video2.show()

        # STOP TIMER THREAD AND RELEASE V0
        self.clear("all", True, True, True)
        self.timer.stop()
        self.video0.release()
        self.video1.release()
        self.video2.release()

        # USED TO CLEAR VIDEO 0, VIDEO 1, VIDEO 2 DATA STRUCTURES
    def clear(self, mode, source0, source1, source2):
        newDeque = deque(maxlen= self.args["buffer"])
        if(mode == "all"):
            print("clearing all");
            if(source0):
                print(" clearing all source0");
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
                print(" clearing all source1");
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
                print(" clearing all source2");
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
            print("clearing red");
            if (source0):
                print(" clearing red source0");
                self.v0_red = {'x': [], 'y': [], 'z': []}
                self.v0_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source1):
                print(" clearing red source1");
                self.v1_red = {'x': [], 'y': [], 'z': []}
                self.v1_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source2):
                print(" clearing red source2");
                self.v2_red = {'x': [], 'y': [], 'z': []}
                self.v2_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

        elif (mode == "green"):
            print("clearing green");
            if (source0):
                print(" clearing green source0");
                self.v0_green = {'x': [], 'y': [], 'z': []}
                self.v0_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source1):
                print(" clearing green source1");
                self.v1_green = {'x': [], 'y': [], 'z': []}
                self.v1_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source2):
                print(" clearing green source2");
                self.v2_green = {'x': [], 'y': [], 'z': []}
                self.v2_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

        elif (mode == "blue"):
            print("clearing blue");
            if (source0):
                print(" clearing blue source0");
                self.v0_blue = {'x': [], 'y': [], 'z': []}
                self.v0_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source1):
                print(" clearing blue source1");
                self.v1_blue = {'x': [], 'y': [], 'z': []}
                self.v1_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source2):
                print(" clearing blue source2");
                self.v2_blue = {'x': [], 'y': [], 'z': []}
                self.v2_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

        elif (mode == "yellow"):
            print("clearing yellow");
            if (source0):
                print(" clearing yellow source0");
                self.v0_yellow = {'x': [], 'y': [], 'z': []}
                self.v0_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source1):
                print(" clearing yellow source1");
                self.v1_yellow = {'x': [], 'y': [], 'z': []}
                self.v1_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

            if (source2):
                print(" clearing yellow source2");
                self.v2_yellow = {'x': [], 'y': [], 'z': []}
                self.v2_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'pts': newDeque}

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

