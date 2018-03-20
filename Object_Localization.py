import argparse

import cv2
import imutils
import numpy as np


def Object_Localization(frame, newPts, newCounter):
    isGreenDetected = False
    isRedDetected = False
    isBlueDetected = False
    isYellowDetected = False

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

    lower = {'yellow': (23, 59, 119), 'green': (66, 122, 129), 'blue': (97, 100, 117),
             'red': (166, 84, 141)}  # assign new item lower['blue'] = (93, 10, 0)
    upper = {'yellow': (54, 255, 255), 'green': (86, 255, 255), 'blue': (117, 255, 255), 'red': (186, 255, 255)}

    # define standard colors for circle around the object
    colors = {'red': (0, 0, 255), 'green': (0, 255, 0), 'blue': (255, 0, 0), 'yellow': (0, 255, 217)}

    pts = newPts
    counter = newCounter
    inches = 0
    (x, y, z) = (0, 0, 0)

    (x_red, x_green, x_blue, x_yellow) = (0, 0, 0, 0)
    (y_red, y_green, y_blue, y_yellow) = (0, 0, 0, 0)
    (z_red, z_green, z_blue, z_yellow) = (0, 0, 0, 0)

    # fig = plt.figure()
    # ax = fig.gca(projection='3d')
    # ax.set_xlabel('X-Direction')
    # ax.set_ylabel('Y-Direction')
    # ax.set_zlabel('Z-Direction')

    # resize the frame, blur it, and convert it to the HSV
    # color space
    thisFrame = imutils.resize(frame, width=600)
    blurredFrame = cv2.GaussianBlur(thisFrame, (11, 11), 0)
    hsv = cv2.cvtColor(thisFrame, cv2.COLOR_BGR2HSV)

    for key, value in upper.items():

        if (key == "red"):
            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            # mask = cv2.inRange(hsv, greenLower, greenUpper)
            kernel = np.ones((9, 9), np.uint8)
            mask = cv2.inRange(hsv, lower[key], upper[key])
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            # mask = cv2.erode(mask, None, iterations=2)
            # mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]

            # and initialize center of the ball
            center = None
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
                if radius > 10:
                    # draw the circle and centroid on the frame
                    # cv2.circle(thisFrame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(thisFrame, (int(x), int(y)), int(radius), colors[key], 2)
                    cv2.circle(thisFrame, center, 5, (0, 0, 255), -1)
                    pts.appendleft(center)
                    isRedDetected = True

                else:
                    isRedDetected = False

        if (key == "yellow"):
            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            # mask = cv2.inRange(hsv, greenLower, greenUpper)
            kernel = np.ones((9, 9), np.uint8)
            mask = cv2.inRange(hsv, lower[key], upper[key])
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            # mask = cv2.erode(mask, None, iterations=2)
            # mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]

            # and initialize center of the ball
            center = None
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
                if radius > 10:
                    # draw the circle and centroid on the frame
                    # cv2.circle(thisFrame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(thisFrame, (int(x), int(y)), int(radius), colors[key], 2)
                    cv2.circle(thisFrame, center, 5, (0, 0, 255), -1)
                    pts.appendleft(center)
                    isYellowDetected = True

                else:
                    isYellowDetected = False

        if (key == "blue"):
            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            # mask = cv2.inRange(hsv, greenLower, greenUpper)
            kernel = np.ones((9, 9), np.uint8)
            mask = cv2.inRange(hsv, lower[key], upper[key])
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            # mask = cv2.erode(mask, None, iterations=2)
            # mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]

            # and initialize center of the ball
            center = None
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
                if radius > 10:
                    # draw the circle and centroid on the frame
                    # cv2.circle(thisFrame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(thisFrame, (int(x), int(y)), int(radius), colors[key], 2)
                    cv2.circle(thisFrame, center, 5, (0, 0, 255), -1)
                    pts.appendleft(center)
                    isBlueDetected = True

                else:
                    isBlueDetected = False

        if (key == "green"):
            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            # mask = cv2.inRange(hsv, greenLower, greenUpper)
            kernel = np.ones((9, 9), np.uint8)
            mask = cv2.inRange(hsv, lower[key], upper[key])
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            # mask = cv2.erode(mask, None, iterations=2)
            # mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]

            # and initialize center of the ball
            center = None
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
                if radius > 10:
                    # draw the circle and centroid on the frame
                    # cv2.circle(thisFrame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(thisFrame, (int(x), int(y)), int(radius), colors[key], 2)
                    cv2.circle(thisFrame, center, 5, (0, 0, 255), -1)
                    pts.appendleft(center)
                    isGreenDetected = True

                else:
                    isGreenDetected = False

        print("\n" + str(key) + " pts length:\t" + str(len(pts)))
        for i in np.arange(1, len(pts)):
            # if either of the tracked points are None, ignore
            if pts[i - 1] is None or pts[i] is None:
                print(" Not Enough Points ")
                continue

            # check to see if enough points have been accumulated in
            # the buffer
            if counter >= 10 and i == 1 and pts[-10] is not None:
                # COMPUTE POINTS AND STORE INTO DATA STRUCTURE
                if isRedDetected:
                    print(" Red Detected ")
                    x_red = pts[-10][0] - pts[i][0]
                    y_red = pts[-10][1] - pts[i][1]
                    z_red = round(inches)
                if isGreenDetected:
                    print(" Green Detected ")
                    x_green = pts[-10][0] - pts[i][0]
                    y_green = pts[-10][1] - pts[i][1]
                    z_green = round(inches)

                if isBlueDetected:
                    print(" Blue Detected ")
                    x_blue = pts[-10][0] - pts[i][0]
                    y_blue = pts[-10][1] - pts[i][1]
                    z_blue = round(inches)

                if isYellowDetected:
                    print(" Yellow Detected ")
                    x_yellow = pts[-10][0] - pts[i][0]
                    y_yellow = pts[-10][1] - pts[i][1]
                    z_yellow = round(inches)

                # x = pts[-10][0] - pts[i][0]
                # y = pts[-10][1] - pts[i][1]
                # z = round(inches)

                # draw the connecting lines
                thickness = int(np.sqrt(args["buffer"] / float(i + 1)))
                cv2.line(thisFrame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # return the frame and increment counter
    counter += 1

    print("----------------------------------------------------------------------------------------------")
    print("COUNTER: " + str(counter) +
          "\t\t\nRED:\t" + str(isRedDetected) + " \t\tx_red:\t\t" + str(x_red) + "\t\ty_red:\t\t" + str(
        y_red) + "\t\tz_red:\t\t" + str(z_red) +
          "\t\t\nGREEN:\t" + str(isGreenDetected) + " \t\tx_green:\t" + str(x_green) + "\t\ty_green:\t" + str(
        y_green) + "\t\tz_green:\t" + str(z_green) +
          "\t\t\nBLUE:\t" + str(isBlueDetected) + " \t\tx_blue:\t\t" + str(x_blue) + "\t\ty_blue:\t\t" + str(
        y_blue) + "\t\tz_blue:\t\t" + str(z_blue) +
          "\t\t\nYELLOW:\t" + str(isYellowDetected) + " \t\tx_yellow:\t" + str(x_yellow) + "\t\ty_yellow:\t" + str(
        y_yellow) + "\t\tz_yellow:\t" + str(z_yellow)
          )

    # print("counter: " + str(counter) + "\tpts: " + str(len(pts)) + " \t\t\tx: " + str(x) + "\t\t\ty: " + str(y) + "\t\t\tz: " + str(z))
    return thisFrame, \
           x_red, y_red, z_red, \
           x_green, y_green, z_green, \
           x_blue, y_blue, z_blue, \
           x_yellow, y_yellow, z_yellow, \
           pts, counter, isRedDetected, isGreenDetected, isBlueDetected, isYellowDetected
