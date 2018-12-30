import argparse

import cv2
import imutils
import numpy as np
from collections import Counter
import math
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

def Localization(v0_frame, v1_frame, v2_frame,
                 v0_blue,v0_yellow,v0_red,v0_green, v0_isDetected,
                 v1_blue,v1_yellow,v1_red,v1_green, v1_isDetected,
                 v2_blue,v2_yellow,v2_red,v2_green, v2_isDetected, global_inches):

    _global_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None, 'isCalculated': False}
    _global_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None, 'isCalculated': False}
    _global_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None, 'isCalculated': False}
    _global_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None, 'isCalculated': False}

    X_REF_POINT  = 200
    Y_REF_POINT = 150
    PIXEL_TRACKING = 5
    BALL_RADIUS = 5
    FRAME_CENTER = (X_REF_POINT,Y_REF_POINT)
    V0_ANGLE = 0
    V1_ANGLE =  90*(math.pi/180)
    V2_ANGLE = 0
    MIN_NUM_POINTS = 10

    KNOWN_DISTANCE = 24.0
    KNOWN_WIDTH = 2.65
    marker = 30

    focalLength =(marker * KNOWN_DISTANCE) / KNOWN_WIDTH



    def calculate_global_x_y(v0_color, v1_color, v2_color):
        try:
            _global_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': 0, 'length1': 0, 'length2': 0, 'isCalculated': False}
            if ((len(v0_color['x']) > MIN_NUM_POINTS) and (len(v1_color['x']) > MIN_NUM_POINTS)): # and (len(v2_color['pts']) > MIN_NUM_POINTS)):
                _global_xyz_pts['length0'] = round((v0_color['x'][-1] - X_REF_POINT) * math.cos(V0_ANGLE) + (v0_color['y'][-1] - Y_REF_POINT) * math.sin(V0_ANGLE))
                _global_xyz_pts['length1'] = round((v1_color['x'][-1] - X_REF_POINT) * math.cos(V1_ANGLE) + (v1_color['y'][-1] - Y_REF_POINT) * math.sin(V1_ANGLE))

            else:
                _global_xyz_pts['isCalculated'] = False
                return
            determinant = (1 / ((math.cos(V0_ANGLE)) * (math.sin(V1_ANGLE)) - (math.sin(V0_ANGLE)) * (math.cos(V1_ANGLE))))
            inverseMatrix = [determinant * round(math.sin(V1_ANGLE)), determinant * round(math.sin(V0_ANGLE))], \
                            [determinant * round(math.cos(V1_ANGLE)), determinant * round(math.cos(V0_ANGLE))]
            GLOBAL_REF_ADD = [
                inverseMatrix[0][0] * _global_xyz_pts['length0'] + inverseMatrix[0][1] * _global_xyz_pts['length1'],
                inverseMatrix[1][0] * _global_xyz_pts['length0'] + inverseMatrix[1][1] * _global_xyz_pts['length1']]

            _global_xyz_pts['x'] = round(X_REF_POINT + GLOBAL_REF_ADD[0])
            _global_xyz_pts['y'] = round(Y_REF_POINT + GLOBAL_REF_ADD[1])
            _global_xyz_pts['z'] = 0
            _global_xyz_pts['isCalculated'] = True
            _global_xyz_pts['x'] = (dis_to_camera_x(focalLength, 67.31, 400, 5.14, _global_xyz_pts['x'])*.039)/100
            _global_xyz_pts['y'] = (dis_to_camera_y(focalLength, 67.31, 300, 3.5, _global_xyz_pts['y'])*.039)/100
            _global_xyz_pts['z'] = global_inches

            return _global_xyz_pts

        except Exception as e:
            print(e)

    def distance_to_camera(knownWidth, focalLength, perWidth):
        # compute and return the distance from the image to camera
        return (knownWidth * focalLength) / perWidth

    def dis_to_camera_x(focalLength, REAL_WIDTH, IMAGE_WIDTH, SENSOR_WIDTH, OBJECT_WIDTH):

        return((focalLength*REAL_WIDTH*IMAGE_WIDTH)/(OBJECT_WIDTH*SENSOR_WIDTH))

    def dis_to_camera_y(focalLength, REAL_HEIGHT, IMAGE_HEIGHT, SENSOR_HEIGHT, OBJECT_HEIGHT):

        return((focalLength*REAL_HEIGHT*IMAGE_HEIGHT)/(OBJECT_HEIGHT*SENSOR_HEIGHT))


    if(v0_isDetected['red'] is True and v1_isDetected['red'] is True):# or v2_isDetected['red']):
        _global_red_xyz_pts = calculate_global_x_y(v0_red, v1_red, v2_red)
    if (v0_isDetected['green'] is True  and v1_isDetected['green'] is True):# or v2_isDetected['green']):

        _global_green_xyz_pts = calculate_global_x_y(v0_green, v1_green, v2_green)

    if (v0_isDetected['blue'] is True and v1_isDetected['blue'] is True):# or v2_isDetected['blue']):
        _global_blue_xyz_pts = calculate_global_x_y(v0_blue, v1_blue, v2_blue)


    if (v0_isDetected['yellow'] is True and v1_isDetected['yellow'] is True):# v2_isDetected['yellow']):
        _global_yellow_xyz_pts = calculate_global_x_y(v0_yellow, v1_yellow, v2_yellow)



    return v0_frame,v1_frame,v2_frame, _global_red_xyz_pts, _global_green_xyz_pts, _global_blue_xyz_pts,_global_yellow_xyz_pts