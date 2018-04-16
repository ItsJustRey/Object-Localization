import argparse

import cv2
import imutils
import numpy as np
from collections import Counter

def Localization(v0_red, v0_green, v0_blue, v0_yellow, v0_frame, v1_red, v1_green, v1_blue, v1_yellow, v2_red, v2_green, v2_blue, v2_yellow):

    X_REF_POINT  = 320
    Y_REF_POINT = 240
    PIXEL_TRACKING = 5
    BALL_RADIUS = 5


    if(len(v0_yellow['x']) > 10):
        last_yellow_index = len(v0_yellow['x'])-1
        #print(v0_red['x'][len(v0_red['x'])-1])

        if(v0_yellow['x'][last_yellow_index] > 0 and
            v0_yellow['y'][last_yellow_index] > 0 and
            v0_yellow['x'][last_yellow_index] > X_REF_POINT and
            v0_yellow['y'][last_yellow_index] > Y_REF_POINT ):

            cv2.circle(v0_frame, (X_REF_POINT + PIXEL_TRACKING , Y_REF_POINT + PIXEL_TRACKING), 5, (0, 0, 255), -1)

        elif(v0_yellow['x'][last_yellow_index] < 0 and v0_yellow['y'][last_yellow_index] <0 ):

            cv2.circle(v0_frame, (X_REF_POINT + PIXEL_TRACKING , Y_REF_POINT + PIXEL_TRACKING), 5, (0, 0, 255), -1)

    #cv2.circle(v0_frame, (,v0_red['y'][2]), BALL_RADIUS, (0, 0, 255), 2)






    return v0_frame

