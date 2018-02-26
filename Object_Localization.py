import argparse


import cv2
import imutils
import numpy as np


def Object_Localization(frame, newPts, newCounter):

    def distance_to_camera(knownWidth, focalLength, perWidth):
        # compute and return the distance from the image to camera
        return (knownWidth * focalLength) / perWidth

    KNOWN_DISTANCE = 24.0
    KNOWN_WIDTH = 2.65
    marker = 30

    focalLength = (marker * KNOWN_DISTANCE) / KNOWN_WIDTH

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
    args = vars(ap.parse_args())

    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space, then initialize the
    # list of tracked points
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)
    pts = newPts
    counter = newCounter
    inches = 0
    (x, y, z) = (0, 0, 0)

    #fig = plt.figure()
    #ax = fig.gca(projection='3d')
    #ax.set_xlabel('X-Direction')
    #ax.set_ylabel('Y-Direction')
    #ax.set_zlabel('Z-Direction')


    # resize the frame, blur it, and convert it to the HSV
    # color space
    thisFrame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(thisFrame, (11, 11), 0)
    hsv = cv2.cvtColor(thisFrame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]

    # and initialize center of the ball
    center = None
    isDetected = False
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # Get distance for Z-axis using reference image (In inches)
        marker = cv2.minAreaRect(c)
        inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])

        # only proceed if the radius meets a minimum size
        if radius > 6:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(thisFrame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(thisFrame, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)
            isDetected = True
        else:
            isDetected = False

    #print("counter: " + str(counter))
    #print("pts: " + str(len(pts)))
    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None:
            continue

        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and pts[-2] is not None:
            # COMPUTE POINTS AND STORE INTO DATA STRUCTURE
            x = pts[-2][0] - pts[i][0]
            y = pts[-2][1] - pts[i][1]
            z = round(inches)

            # draw the connecting lines
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(thisFrame, pts[i - 1], pts[i], (0, 0, 255), thickness)


    # return the frame and increment counter
    counter += 1
    return thisFrame, x, y, z, pts, counter, isDetected
