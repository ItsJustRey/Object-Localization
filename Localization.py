import argparse

import cv2
import imutils
import numpy as np
from collections import Counter
import math

def Localization(v0_frame, v1_frame, v2_frame,
            v0_blue_xyz_pts,v0_yellow_xyz_pts,v0_red_xyz_pts,v0_green_xyz_pts, v0_isDetected,
            v1_blue_xyz_pts,v1_yellow_xyz_pts,v1_red_xyz_pts,v1_green_xyz_pts, v1_isDetected,
            v2_blue_xyz_pts,v2_yellow_xyz_pts,v2_red_xyz_pts,v2_green_xyz_pts, v2_isDetected):

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
    def calculate_global_x_y(v0_xyz_pts, v1_xyz_pts, v2_xyz_pts):
        try:
            print("PEASE")
            _global_xyz_pts = {'x': None, 'y': None, 'z': None, 'length0': None, 'length1': None, 'length2': None}
            print("here0.1")
            if ((len(v0_xyz_pts['pts']) > MIN_NUM_POINTS) and (len(v1_xyz_pts['pts']) > MIN_NUM_POINTS) and (len(v2_xyz_pts['pts']) > MIN_NUM_POINTS)):
                _global_xyz_pts['length0'] = (v0_xyz_pts['x'][1] - X_REF_POINT) * math.cos(V0_ANGLE) + \
                                                  (v0_xyz_pts['y'][1] - Y_REF_POINT) * math.sin(V0_ANGLE)
                print("here0.2")
                _global_xyz_pts['length1'] = (v1_xyz_pts['x'][1] - X_REF_POINT) * math.cos(V1_ANGLE) + \
                                                  (v1_xyz_pts['y'][1] - Y_REF_POINT) * math.sin(V1_ANGLE)
            else:
                return
            print("here0.3")
            determinant = (1 / ((math.cos(V0_ANGLE)) * (math.sin(V1_ANGLE)) - (math.sin(V0_ANGLE)) * (math.cos(V1_ANGLE))))
            print("here0")
            print(determinant)
            inverseMatrix = [determinant * round(math.sin(V1_ANGLE)), determinant * round(math.sin(V0_ANGLE))], \
                            [determinant * round(math.cos(V1_ANGLE)), determinant * round(math.cos(V0_ANGLE))]
            print("here1")
            print(inverseMatrix)

            GLOBAL_REF_ADD = [
                inverseMatrix[0][0] * _global_xyz_pts['length0'] + inverseMatrix[0][1] * _global_xyz_pts[
                    'length1'],
                inverseMatrix[1][0] * _global_xyz_pts['length0'] + inverseMatrix[1][1] * _global_xyz_pts[
                    'length1']]
            print("here2")
            _global_xyz_pts['x'] = round(X_REF_POINT + GLOBAL_REF_ADD[0])
            _global_xyz_pts['y'] = round(Y_REF_POINT + GLOBAL_REF_ADD[1])
            print(str(_global_xyz_pts['length0']))
            print(str(_global_xyz_pts['x']))
            print(str(_global_xyz_pts['y']))
            print("here3")
            return _global_xyz_pts

        except Exception as e:
            print(e)



    print("HERE")
    if(v0_isDetected['red'] is True and v1_isDetected['red'] is True):# or v2_isDetected['red']):
        _global_red_xyz_pts = calculate_global_x_y(v0_red_xyz_pts, v1_red_xyz_pts, v2_red_xyz_pts)
    if (v0_isDetected['green'] is True  and v1_isDetected['green'] is True):# or v2_isDetected['green']):

        _global_green_xyz_pts = calculate_global_x_y(v0_green_xyz_pts, v1_green_xyz_pts, v2_green_xyz_pts)
    #if (v0_isDetected['blue'] is True and v1_isDetected['blue'] is True):# or v2_isDetected['blue']):
    _global_blue_xyz_pts = calculate_global_x_y(v0_blue_xyz_pts, v1_blue_xyz_pts, v2_blue_xyz_pts)
    #print(_global_blue_xyz_pts)
    #else

        # _global_blue_xyz_pts['length0'] = (v0_blue_xyz_pts['x'][-1] - X_REF_POINT) * math.cos(V0_ANGLE) +\
        #                                  (v0_blue_xyz_pts['y'][-1] - Y_REF_POINT) * math.sin(V0_ANGLE)
        #
        # _global_blue_xyz_pts['length1'] = (v1_blue_xyz_pts['x'][-1] - X_REF_POINT) * math.cos(V1_ANGLE) +\
        #                                  (v1_blue_xyz_pts['y'][-1] - Y_REF_POINT) * math.sin(V1_ANGLE)
        #
        # determinant = (1 / ((math.cos(V0_ANGLE)) * (math.sin(V1_ANGLE)) - (math.sin(V0_ANGLE)) * (math.cos(V1_ANGLE))))
        # print(determinant)
        # inverseMatrix = [determinant * round(math.sin(V1_ANGLE)), determinant * round(math.sin(V0_ANGLE))], \
        #                 [determinant * round(math.cos(V1_ANGLE)), determinant * round(math.cos(V0_ANGLE))]
        #
        # print(inverseMatrix)
        #
        # GLOBAL_REF_ADD = [inverseMatrix[0][0]*_global_blue_xyz_pts['length0']+ inverseMatrix[0][1]*_global_blue_xyz_pts['length1'],
        #                   inverseMatrix[1][0]*_global_blue_xyz_pts['length0']+ inverseMatrix[1][1]*_global_blue_xyz_pts['length1']]
        #
        # _global_blue_xyz_pts['x'] = X_REF_POINT + GLOBAL_REF_ADD[0]
        # _global_blue_xyz_pts['y'] = Y_REF_POINT + GLOBAL_REF_ADD[1]




    if (v0_isDetected['yellow'] is True and v1_isDetected['yellow'] is True):# v2_isDetected['yellow']):
        _global_yellow_xyz_pts = calculate_global_x_y(v0_yellow_xyz_pts, v1_yellow_xyz_pts, v2_yellow_xyz_pts)


    # if(len(v0_yellow['x']) > 10):
    #     last_yellow_index = len(v0_yellow['x'])-1
    #     #print(v0_red['x'][len(v0_red['x'])-1])
    #
    #     if(v0_yellow['x'][last_yellow_index] > 0 and
    #         v0_yellow['y'][last_yellow_index] > 0 and
    #         v0_yellow['x'][last_yellow_index] > X_REF_POINT and
    #         v0_yellow['y'][last_yellow_index] > Y_REF_POINT ):
    #
    #         cv2.circle(v0_frame, (X_REF_POINT + PIXEL_TRACKING , Y_REF_POINT + PIXEL_TRACKING), 5, (0, 0, 255), -1)
    #
    #     elif(v0_yellow['x'][last_yellow_index] < 0 and v0_yellow['y'][last_yellow_index] <0 ):
    #
    #         cv2.circle(v0_frame, (X_REF_POINT + PIXEL_TRACKING , Y_REF_POINT + PIXEL_TRACKING), 5, (0, 0, 255), -1)



    #cv2.circle(v0_frame, (,v0_red['y'][2]), BALL_RADIUS, (0, 0, 255), 2)

    for i in range(1, len(v0_blue_xyz_pts['pts'])):
        thickness=1
        cv2.line(v0_frame,FRAME_CENTER, v0_blue_xyz_pts['pts'][i],(255, 0, 0), thickness)

    for i in range(1, len(v0_red_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v0_frame, FRAME_CENTER, v0_red_xyz_pts['pts'][i], (0, 0, 255), thickness)

    for i in range(1, len(v0_green_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v0_frame, FRAME_CENTER, v0_green_xyz_pts['pts'][i], (0, 255, 0), thickness)

    for i in range(1, len(v0_yellow_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v0_frame,FRAME_CENTER, v0_yellow_xyz_pts['pts'][i], (0, 255, 255), thickness)

##########################################################################################################################

    for i in range(1, len(v1_blue_xyz_pts['pts'])):
        thickness=1
        cv2.line(v1_frame,FRAME_CENTER, v1_blue_xyz_pts['pts'][i],(255, 0, 0), thickness)

    for i in range(1, len(v1_red_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v1_frame, FRAME_CENTER, v1_red_xyz_pts['pts'][i], (0, 0, 255), thickness)

    for i in range(1, len(v1_green_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v1_frame, FRAME_CENTER, v1_green_xyz_pts['pts'][i], (0, 255, 0), thickness)

    for i in range(1, len(v1_yellow_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v1_frame,FRAME_CENTER, v1_yellow_xyz_pts['pts'][i], (0, 255, 255), thickness)

##########################################################################################################################

    for i in range(1, len(v2_blue_xyz_pts['pts'])):
        thickness=1
        cv2.line(v2_frame,FRAME_CENTER, v2_blue_xyz_pts['pts'][i],(255, 0, 0), thickness)

    for i in range(1, len(v2_red_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v2_frame, FRAME_CENTER, v2_red_xyz_pts['pts'][i], (0, 0, 255), thickness)

    for i in range(1, len(v2_green_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v2_frame, FRAME_CENTER, v2_green_xyz_pts['pts'][i], (0, 255, 0), thickness)

    for i in range(1, len(v2_yellow_xyz_pts['pts'])):
        thickness = 1
        cv2.line(v2_frame,FRAME_CENTER, v2_yellow_xyz_pts['pts'][i], (0, 255, 255), thickness)

    return v0_frame,v1_frame,v2_frame

