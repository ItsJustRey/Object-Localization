# import the necessary packages
import argparse
import os
from Tkinter import *
from collections import deque

import cv2
import imutils
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PIL import ImageTk


class Application(Frame):
    def __init__(self, master= None):
        Frame.__init__(self, master)
        """ Initialize application which uses OpenCV + Tkinter. It displays a video stream in a Tkinter window  """

        # for r in range(6):
        #     self.master.rowconfigure(r, weight=1)
        #
        # for c in range(5):
        #     self.master.columnconfigure(c, weight=1)

        self.vs = cv2.VideoCapture(0) # capture video frames, 0 is your default video camera
        self.current_image = None  # current image from the camera

        self.vs1 = cv2.VideoCapture(1) # capture video frames, 0 is your default video camera
        self.current_image1 = None  # current image from the camera

        Frame1 = Frame(master, width=720, height=480, bg="green")
        Frame1.pack(fill='none', expand=True, side="left")

        Frame2 = Frame(master, width=720, height=480, bg="blue")
        Frame2.pack(fill='none', expand=True, side="right")

        self.master.title("Object Localization")  # set window title
        # self.destructor function gets fired when the window is closed
        self.master.protocol('WM_DELETE_WINDOW', self.destructor)
        self.panel = Label(Frame1)  # initialize image panel
        self.panel.pack(padx=10, pady=10)
        self.master.config(cursor="arrow")

        self.panel = Label(Frame2)  # initialize image panel
        self.panel.pack(padx=10, pady=10)
        self.master.config(cursor="arrow")





        # create a button, that when pressed, will take the current frame and save it to file
        btn2 = Button(self.master, text="Stop", command=self.take_snapshot)
        btn2.pack(side="bottom", fill="both", expand=False, padx=10, pady=10)

        btn = Button(self.master, text="Start", command=self.destructor)
        btn.pack(side="bottom", fill="both", expand=False, padx=10, pady=10)

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame

        self.video_loop()
        #self.video_loop1()


    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        frame = cv2.resize(frame, (480, 360))
        if ok:  # frame captured without any errors
            key = cv2.waitKey(1000)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            self.current_image = self.current_image.resize([480, 360])
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image

        self.master.after(1, self.video_loop)  # call the same function after 30 milliseconds

    def video_loop1(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame1 = self.vs1.read()  # read frame from video stream
        #frame1 = cv2.resize(frame1, (480, 360))
        if ok:  # frame captured without any errors
            key = cv2.waitKey(1000)
            cv2image = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image1 = Image.fromarray(cv2image)  # convert image for PIL
            self.current_image1 = self.current_image1.resize([480, 360])
            imgtk1 = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk1 = imgtk1  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk1)  # show the image

        self.master.after(1, self.video_loop1)  # call the same function after 30 milliseconds






    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        os.system('C:\Users\\rishi\PycharmProjects\Track_Obj\obj.py')



    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing window...")
        self.master.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
                help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
root = Tk()
pba = Application(master=root)
pba.master.mainloop()


# Z-Axis stuff
class Object_Local(Application):

    def find_marker(image):
        # convert the image to grayscale and blue to detect edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5,5), 0)
        edged = cv2.Canny(gray,35,125)

        # find the contours in the edged image
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APROX_SIMPLE)
        c = max(cnts, key=cv2.contourArea)
        return cv2.minAreaRect(c)

def distance_to_camera(knownWidth, focalLength, perWidth):
    #compute and return the distance from the image to camera
    return (knownWidth * focalLength) / perWidth

#Known distance and width from reference photo
KNOWN_DISTANCE = 24.0
KNOWN_WIDTH = 2.65
marker = 30


#!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!
focalLength = (marker * KNOWN_DISTANCE) / KNOWN_WIDTH

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=128,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])
xArray = []
yArray = []
zArray = []
counter = 0
(dX, dY, dZ) = (0,0,0)
direction =""
fig = plt.figure()
ax = fig.gca(projection='3d')
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])

    # keep looping
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
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
        if radius > 1:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)

    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and pts[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # text variables
            dX = pts[-2][0] - pts[i][0]
            xArray.append(dX)
            dY = pts[-2][1] - pts[i][1]
            yArray.append(dY)
            # get Z-coordinate in inches
            dZ=inches
            zArray.append(dZ)
            (dirX, dirY, dirZ) = ("", "", "")


            # draw the connecting lines
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the movement deltas and the direction of movement on
    # the frame
    cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 0, 255), 3)
    cv2.putText(frame, "dx: {}, dy: {}, dz: {}".format(dX, dY, dZ),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)

    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    counter += 1

    #plt.plot(dX, dY, "ro")
    #plt.xlabel('X-Direction')
    #plt.ylabel('Y-Direction')


# plot data
    ax.set_xlim(-255, 255)
    ax.set_ylim(-255, 255)
    ax.set_zlim(-255, 255)
    ax.set_xlabel('X-Direction')
    ax.set_ylabel('Y-Direction')
    ax.set_zlabel('Z-Direction')
    ax.plot(xArray, yArray, zArray, label='Spatial Coordinates')
    ax.set_color_cycle('black')
    plt.pause(0.001)
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows

ax.legend()
camera.release()
cv2.destroyAllWindows()
