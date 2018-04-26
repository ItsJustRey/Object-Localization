import argparse

import cv2
import imutils
import numpy as np
from collections import Counter
import math

def Localization(v0_frame, v1_frame, v2_frame,
            v0_blue,v0_yellow,v0_red,v0_green, v0_isDetected,
            v1_blue,v1_yellow,v1_red,v1_green, v1_isDetected,
            v2_blue,v2_yellow,v2_red,v2_green, v2_isDetected):

    _global_red_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None}
    _global_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None}
    _global_blue_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None}
    _global_yellow_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None}

    X_REF_POINT  = 200
    Y_REF_POINT = 150
    PIXEL_TRACKING = 5
    BALL_RADIUS = 5
    FRAME_CENTER = (X_REF_POINT,Y_REF_POINT)
    V0_ANGLE = 0
    V1_ANGLE =  90*(math.pi/180)
    V2_ANGLE = 0
    MIN_NUM_POINTS = 10


    def calculate_global_x_y(v0_color, v1_color, v2_color):
        try:
            _global_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': 0, 'length1': 0, 'length2': 0}
            print("here0.1")
            if ((len(v0_color['x']) > MIN_NUM_POINTS) and (len(v1_color['x']) > MIN_NUM_POINTS)): # and (len(v2_color['pts']) > MIN_NUM_POINTS)):
                print("here0.11")
                _global_xyz_pts['length0'] = (v0_color['x'][-1] - X_REF_POINT) * round(math.cos(V0_ANGLE)) + (v0_color['y'][-1] - Y_REF_POINT) * round(math.sin(V0_ANGLE))
                print("here0.12")
                _global_xyz_pts['length1'] = (v1_color['x'][-1] - X_REF_POINT) * math.cos(V1_ANGLE) + \
                                                  (v1_color['y'][-1] - Y_REF_POINT) * math.sin(V1_ANGLE)
            else:
                print("NOT ENOUGH")
                return
            print("here0.2")
            determinant = (1 / ((math.cos(V0_ANGLE)) * (math.sin(V1_ANGLE)) - (math.sin(V0_ANGLE)) * (math.cos(V1_ANGLE))))
            print("here3")
            print(determinant)
            inverseMatrix = [determinant * round(math.sin(V1_ANGLE)), determinant * round(math.sin(V0_ANGLE))], \
                            [determinant * round(math.cos(V1_ANGLE)), determinant * round(math.cos(V0_ANGLE))]
            print("here4")
            print(inverseMatrix)

            GLOBAL_REF_ADD = [
                inverseMatrix[0][0] * _global_xyz_pts['length0'] + inverseMatrix[0][1] * _global_xyz_pts['length1'],
                inverseMatrix[1][0] * _global_xyz_pts['length0'] + inverseMatrix[1][1] * _global_xyz_pts['length1']]
            print("here5")
            _global_xyz_pts['x'] = round(X_REF_POINT + GLOBAL_REF_ADD[0])
            _global_xyz_pts['y'] = round(Y_REF_POINT + GLOBAL_REF_ADD[1])
            print(str(_global_xyz_pts['length0']))
            print(str(_global_xyz_pts['x']))
            print(str(_global_xyz_pts['y']))
            print("here6")
            return _global_xyz_pts

        except Exception as e:
            print(e)



    print("HERE")
    if(v0_isDetected['red'] is True and v1_isDetected['red'] is True):# or v2_isDetected['red']):
        _global_red_xyz_pts = calculate_global_x_y(v0_red, v1_red, v2_red)
    if (v0_isDetected['green'] is True  and v1_isDetected['green'] is True):# or v2_isDetected['green']):

        _global_green_xyz_pts = calculate_global_x_y(v0_green, v1_green, v2_green)

    if (v0_isDetected['blue'] is True and v1_isDetected['blue'] is True):# or v2_isDetected['blue']):
        _global_blue_xyz_pts = calculate_global_x_y(v0_blue, v1_blue, v2_blue)
        print(_global_blue_xyz_pts)


    if (v0_isDetected['yellow'] is True and v1_isDetected['yellow'] is True):# v2_isDetected['yellow']):
        _global_yellow_xyz_pts = calculate_global_x_y(v0_yellow, v1_yellow, v2_yellow)


#     for i in range(1, len(v0_blue['pts'])):
#         thickness=1
#         cv2.line(v0_frame,FRAME_CENTER, v0_blue['pts'][i],(255, 0, 0), thickness)
#
#     for i in range(1, len(v0_red['pts'])):
#         thickness = 1
#         cv2.line(v0_frame, FRAME_CENTER, v0_red['pts'][i], (0, 0, 255), thickness)
#
#     for i in range(1, len(v0_green['pts'])):
#         thickness = 1
#         cv2.line(v0_frame, FRAME_CENTER, v0_green['pts'][i], (0, 255, 0), thickness)
#
#     for i in range(1, len(v0_yellow['pts'])):
#         thickness = 1
#         cv2.line(v0_frame,FRAME_CENTER, v0_yellow['pts'][i], (0, 255, 255), thickness)
#
# ##########################################################################################################################
#
#     for i in range(1, len(v1_blue['pts'])):
#         thickness=1
#         cv2.line(v1_frame,FRAME_CENTER, v1_blue['pts'][i],(255, 0, 0), thickness)
#
#     for i in range(1, len(v1_red['pts'])):
#         thickness = 1
#         cv2.line(v1_frame, FRAME_CENTER, v1_red['pts'][i], (0, 0, 255), thickness)
#
#     for i in range(1, len(v1_green['pts'])):
#         thickness = 1
#         cv2.line(v1_frame, FRAME_CENTER, v1_green['pts'][i], (0, 255, 0), thickness)
#
#     for i in range(1, len(v1_yellow['pts'])):
#         thickness = 1
#         cv2.line(v1_frame,FRAME_CENTER, v1_yellow['pts'][i], (0, 255, 255), thickness)
#
# ##########################################################################################################################
#
#     for i in range(1, len(v2_blue['pts'])):
#         thickness=1
#         cv2.line(v2_frame,FRAME_CENTER, v2_blue['pts'][i],(255, 0, 0), thickness)
#
#     for i in range(1, len(v2_red['pts'])):
#         thickness = 1
#         cv2.line(v2_frame, FRAME_CENTER, v2_red['pts'][i], (0, 0, 255), thickness)
#
#     for i in range(1, len(v2_green['pts'])):
#         thickness = 1
#         cv2.line(v2_frame, FRAME_CENTER, v2_green['pts'][i], (0, 255, 0), thickness)
#
#     for i in range(1, len(v2_yellow['pts'])):
#         thickness = 1
#         cv2.line(v2_frame,FRAME_CENTER, v2_yellow['pts'][i], (0, 255, 255), thickness)

    return v0_frame,v1_frame,v2_frame

