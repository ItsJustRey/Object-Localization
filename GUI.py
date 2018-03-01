from Tkinter import *
import argparse
import cv2
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageTk
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from mpl_toolkits import mplot3d
import Object_Localization
from collections import deque
matplotlib.use('TkAgg')
style.use("ggplot")

class GUI(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        Tk.wm_title(self, "Object Localization")
        self.state('zoomed')
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
        self.vs0.release()
        cv2.destroyAllWindows()

class MainMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        label = Label(self, text = "Main Menu")
        label.pack(pady = 10, padx = 10)

        button_view_video = Button(self, pady = 10, padx = 10, text = "View Video",command = lambda: controller.show_frame(VideoWindow0)).pack()
        button_saved_results = Button(self, pady = 10, padx = 10, text="Saved Results", command=lambda: controller.show_frame(VideoWindow1)).pack()
        #button_video2 = Button(self, text="Video Source 2", command=lambda: controller.show_frame(VideoWindow2)).pack()

class VideoWindow0(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Video Stream")
        label.pack(pady=10, padx=10)
        btn_back = Button(self, pady=10, padx=10, text = "Back", command = lambda: controller.show_frame(MainMenu)).pack(side = "top")
        btn_start = Button(self, pady=10, padx=10, text= "Start", command=lambda: self.v0_loop()).pack(side = "top")
        btn_clear = Button(self, pady=10, padx=10, text="Clear", command=lambda: self.v0_clear()).pack(side = "top")
        btn_start = Button(self, pady=10, padx=10, text="Save", command=lambda: self.v0_save()).pack(side = "top")

        #label.grid(column=2, row=0)
        #btn_back = Button(self, text = "Back", command = lambda: controller.show_frame(MainMenu)).grid(column=1, row=1)
        #btn_start = Button(self, text= "Start", command=lambda: self.v0_loop()).grid(column=2, row=1)
        #btn_clear = Button(self, text="Clear", command=lambda: self.v0_clear()).grid(column=3, row=1)
        #btn_start = Button(self, text="Save", command=lambda: self.v0_save()).grid(column=4, row=1)


        self.vs0 = cv2.VideoCapture(0)
        self.current_image1 = None
        self.isDetected = False
        frame0 = Frame(self, width=400, height= 300, bg="red")
        frame0.pack(side="left")
        #frame0.grid(column=1, row=2)
        frame1 = Frame(self, width=400, height=300, bg="blue")
        frame1.pack(side="left")
        #frame1.grid(column=2, row=2)
        frame2 = Frame(self, width=400, height=300, bg="green")
        frame2.pack(side="left")
        #frame2.grid(column=3, row=2)

        self.panel0 = Label(frame0)
        #self.panel0.grid(column=1, row=1)
        self.panel0.pack(padx=5, pady=5)
        self.panel0.pack(side="left", anchor = "w")

        self.panel1 = Label(frame1)
        #self.panel1.grid(column=2, row=1)
        self.panel1.pack(padx=5, pady=5)
        self.panel1.pack(side="left", anchor = "w")

        self.panel2 = Label(frame2)  # initialize image panel
        #self.panel2.grid(column=3, row=1)
        self.panel2.pack(padx=5, pady=5)
        self.panel2.pack(side="left", anchor = "w")  # initialize image panel


        self.master.config(cursor="arrow")

        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video", help="path to the (optional) video file")
        ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
        self.args = vars(ap.parse_args())



        self.fig = plt.figure()
        self.ax = plt.axes(projection='3d')
        self.v0_clear()

        self.canvas = FigureCanvasTkAgg(self.fig, self)

        self.canvas.show()
        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", anchor = "n")
        #self.canvas.get_tk_widget().grid(column=2, row=3)



    def v0_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        isReady, frame0 = self.vs0.read()  # read frame from video stream
        (frame0, self.v0_x, self.v0_y, self.v0_z, self.pts, self.counter, self.isDetected) = Object_Localization.Object_Localization(frame0, self.pts, self.counter)

        if(self.isDetected):

            if (len(self.pts) > 10):
                self.v0_xArray.append(self.v0_x)
                self.v0_yArray.append(self.v0_y)
                self.v0_zArray.append(self.v0_z)

        else:
            self.v0_clear()

        if isReady:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image1 = Image.fromarray(cv2image)  # convert image for PIL
            #self.current_image1 = self.current_image1.resize([480, 360])
            self.current_image1 = self.current_image1.resize([320, 240])
            imgtk1 = ImageTk.PhotoImage(image=self.current_image1)  # convert image for tkinter

            self.panel0.imgtk1 = imgtk1  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel0.config(image=imgtk1)  # show the image

            self.panel1.imgtk1 = imgtk1  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel1.config(image=imgtk1)  # show the image

            self.panel2.imgtk1 = imgtk1  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel2.config(image=imgtk1)  # show the image

            self.ax.plot(self.v0_xArray, self.v0_zArray, self.v0_yArray, 'black')
            self.canvas.draw_idle()

        self.master.after(33, self.v0_loop)  # call the same function after 30 milliseconds

    def v0_clear(self):
        self.v0_xArray = []
        self.v0_yArray = []
        self.v0_zArray = []
        self.v0_x = None
        self.v0_y = None
        self.v0_z = None
        self.counter = 0
        self.pts = deque(maxlen=self.args["buffer"])
        self.ax.clear()
        self.ax.set_xlabel('X-Direction')
        self.ax.set_ylabel('Y-Direction')
        self.ax.set_zlabel('Z-Direction')
        self.ax.set_xlim(-300, 300)
        self.ax.set_ylim(-300, 300)
        self.ax.set_zlim(-300, 300)
        return

    def v0_save(self):

        return


class VideoWindow1(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Video Source 1")
        label.pack(pady=10, padx=10)

        button_back = Button(self, text="Back", command=lambda: controller.show_frame(MainMenu))
        button_back.pack()

        self.vs1 = cv2.VideoCapture(1)
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

class VideoWindow2(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Video Source 2")
        label.pack(pady=10, padx=10)

        button_back = Button(self, text="Back", command=lambda: controller.show_frame(MainMenu))
        button_back.pack()

        self.vs2 = cv2.VideoCapture(2)
        self.current_image1 = None

        frame1 = Frame(self, width=1080, height=560, bg="blue")
        frame1.pack(fill='none', expand=True, side="left")

        self.panel = Label(frame1)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        self.panel.pack(side="left", fill="both", expand=True)  # initialize image panel
        self.master.config(cursor="arrow")

        self.video_loop2()


    def video_loop2(self):
        """ Get frame from the video stream and show it in Tkinter """
        isReady, frame2 = self.vs2.read()  # read frame from video stream
        frame2 = Object_Localization.Object_Localization(frame2)

        if isReady:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
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