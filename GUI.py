import Object_Localization
import cv2
import numpy as np
from Tkinter import *
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from PIL import Image
from PIL import ImageTk
from mpl_toolkits.mplot3d import Axes3D
import math
from matplotlib.figure import Figure
matplotlib.use('TkAgg')

class GUI(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        Tk.wm_title(self, "Object Localization")

        container = Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainMenu, VideoWindow0, VideoWindow0_Plot):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(MainMenu)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def destructor(self):
        print("[INFO] closing window...")
        self.master.destroy()
        self.vs1.release()
        cv2.destroyAllWindows()

class MainMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        label = Label(self, text = "Main Menu")
        label.pack(pady = 10, padx = 10)

        button_video0 = Button(self, text = "Start Video 0", command = lambda: controller.show_frame(VideoWindow0))
        button_video0.pack()

        button_video1 = Button(self, text="Start Video 1", command=lambda: controller.show_frame(VideoWindow1))
        button_video1.pack()

class VideoWindow0(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Video Source 1")
        label.pack(pady=10, padx=10)

        button_back = Button(self, text = "Back", command = lambda: controller.show_frame(MainMenu))
        button_back.pack()
        button_show_plot = Button(self, text="Show Plot", command=lambda: controller.show_frame(VideoWindow0_Plot))
        button_show_plot.pack()

        self.vs0 = cv2.VideoCapture(1)
        self.current_image1 = None

        frame0 = Frame(self, width=1080, height=560, bg="blue")
        frame0.pack(fill='none', expand=True, side="left")

        self.panel = Label(frame0)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        self.panel.pack(side = "left", fill="both", expand=True)  # initialize image panel
        self.master.config(cursor="arrow")

        #fig = Figure(figsize=(5, 5), dpi=100)
        #a = fig.add_subplot(111)
        #a = fig.gca(projection='3d')
        #ax = fig.gca(projection='3d')
        #a.set_xlabel('X-Direction')
        #a.set_ylabel('Y-Direction')
        #a.set_zlabel('Z-Direction')
        #a.set_xlim(-400, 400)
        #a.set_ylim(-400, 400)
        #a.set_zlim(-400, 400)
        #a.legend()
        #a.plot([0,0,0], [1,1,1], [0,0,0] , 'r', label='Spatial Coordinates')


        fig = Figure(figsize=(5, 5), dpi=100)
        a = fig.add_subplot(111)
        a.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.show()

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)



        self.video_loop0()

    def video_loop0(self):
        """ Get frame from the video stream and show it in Tkinter """
        isReady, frame0 = self.vs0.read()  # read frame from video stream
        frame0 = Object_Localization.Object_Localization(frame0)

        if isReady:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image1 = Image.fromarray(cv2image)  # convert image for PIL
            self.current_image1 = self.current_image1.resize([480, 360])
            imgtk1 = ImageTk.PhotoImage(image=self.current_image1)  # convert image for tkinter

            self.panel.imgtk1 = imgtk1  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk1)  # show the image

        self.master.after(1, self.video_loop0)  # call the same function after 30 milliseconds



class VideoWindow1(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Video Source 1")
        label.pack(pady=10, padx=10)

        button_back = Button(self, text="Back", command=lambda: controller.show_frame(MainMenu))
        button_back.pack()

        self.vs1 = cv2.VideoCapture(0)
        self.current_image1 = None

        frame1 = Frame(self, width=1080, height=560, bg="blue")
        frame1.pack(fill='none', expand=True, side="left")

        self.panel = Label(frame1)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        self.panel.pack(side="left", fill="both", expand=True)  # initialize image panel
        self.master.config(cursor="arrow")

        self.video_loop1()


    def video_loop1(self):
        """ Get frame from the video stream and show it in Tkinter """
        isReady, frame1 = self.vs1.read()  # read frame from video stream
        frame1 = Object_Localization.Object_Localization(frame1)

        if isReady:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image1 = Image.fromarray(cv2image)  # convert image for PIL
            self.current_image1 = self.current_image1.resize([480, 360])
            imgtk1 = ImageTk.PhotoImage(image=self.current_image1)  # convert image for tkinter

            self.panel.imgtk1 = imgtk1  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk1)  # show the image

        self.master.after(1, self.video_loop1)  # call the same function after 30 milliseconds


class VideoWindow0_Plot(Frame):

    def __init__(self, master, controller):
        Frame.__init__(self, master)

        label = Label(self, text="Plot from Video Source 1")
        label.pack(pady=10, padx=10)

        button_back = Button(self, text="Back", command=lambda: controller.show_frame(VideoWindow0))
        button_back.pack()




        #canvas._tkcanvas.pack(side = "top", fill = "both", expand = True)