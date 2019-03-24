import pymongo
from pprint import pprint
import sys, os
import boto3
import gridfs
import cv2
import botocore
import re
from bson import Binary
from PIL import Image
import glob
import os
import shutil

VIDEO_PATH = "./videos/"
VIDEO_NEW_PATH = "./videos/new/"

class Database:

    #define dictionaries to be returned to user
    str_n = "0"

    _global_points_red = {}
    _global_points_green = {}
    _global_points_blue = {}
    _global_points_yellow = {}


    def __init__(self):

        # MongoDB connection
        self.mongo_uri = ""
        self.mongo_connection = None

        # Amazon AWS S3 connection
        self.s3_access_key_id = ""
        self.s3_secret_access_key = ""
        self.s3_bucket_name = ""
        self.s3 = None


    def connect(self):
        """ Connect to database """
        try:
            # MongoDB connection
            self.mongo_connection = pymongo.MongoClient(self.mongo_uri)
            # Issue the serverStatus command and print the results
            serverStatusResult = self.mongo_connection.admin.command("serverStatus")
            pprint(serverStatusResult)

            #Amazon AWS S3 connection
            self.s3 = boto3.resource('s3',
                                     aws_access_key_id=self.s3_access_key_id,
                                     aws_secret_access_key=self.s3_secret_access_key)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

    def insert(self, date, time, frame0, frame1, frame2, red, green, blue, yellow):
        """ Insert data into database """
        try:
            # CREATE KEY FOR EACH FRAME/IMAGE
            frame0_key = "%s_%s_%s%s" % ("V0", date, time,".jpg")
            frame1_key = "%s_%s_%s" % ("V1", date, time)
            frame2_key = "%s_%s_%s" % ("V2", date, time)
            # image0 = Image.open(frame0)
            # image1 = Image.open(frame1)
            # image2 = Image.open(frame2)
            #
            # fs = gridfs.GridFS(db)

            values = {
                'date': date,
                'time': time,
                'frame0': frame0_key,
                'frame1': frame1_key,
                'frame2': frame2_key,
                'red': red,
                'green': green,
                'blue': blue,
                'yellow': yellow
            }
            inserted_ball = self.mongo_connection.objects.balls.insert_one(values)
            print("Inserted " + str(values) + " with _id: " + str(inserted_ball.inserted_id))

            cv2.imwrite('upload.jpg', frame0)
            #cv2.imwrite('upload2.jpg', frame0)
            #cv2.imwrite('upload3.jpg', frame0)

            with open("upload.jpg", 'rb') as image:
                self.s3.Bucket(self.s3_bucket_name).put_object(Key = frame0_key , Body = image)

                # with open("upload.jpg", 'rb') as image:
                #     self.s3.Bucket(self.s3_bucket_name).put_object(Key = frame0_key , Body = image)
                # with open("upload.jpg", 'rb') as image:
                #     self.s3.Bucket(self.s3_bucket_name).put_object(Key = frame0_key , Body = image)

                #self.s3.Bucket(self.s3_bucket_name).put_object(Key = "icy_test_DJIBRIL_GOT_DRUGS.jpg" , Body = image)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)



    def get(self, isRedDetected, isGreenDetected, isBlueDetected, isYellowDetected, dateTimeFrom, dateTimeTo, videoName):

        global _global_points_red
        global _global_points_green
        global _global_points_blue
        global _global_points_yellow

        _global_points_red=  {'x': None, 'y': None, 'z': None}
        _global_points_green= {'x': None, 'y': None, 'z': None}
        _global_points_blue= {'x': None, 'y': None, 'z': None}
        _global_points_yellow= {'x': None, 'y': None, 'z': None}
        _frame_0_key = {'key': None}

        red_x_points = []
        red_y_points = []
        red_z_points = []
        green_x_points = []
        green_y_points = []
        green_z_points = []
        blue_x_points = []
        blue_y_points = []
        blue_z_points = []
        yellow_x_points = []
        yellow_y_points = []
        yellow_z_points = []
        _frame_0 = []
        global str_n
        str_n = "0"

        print(" red: " + str(isRedDetected))
        print(" green: " + str(isGreenDetected))
        print(" blue: " + str(isBlueDetected))
        print(" yellow: " + str(isYellowDetected))

        #date_frmt = date.strftime("%Y-%m-%d")


        try:
            print("date inside get(): " + dateTimeFrom)
            values = {
                "date": dateTimeFrom,
                "red.isCalculated": isRedDetected,
                "green.isCalculated": isGreenDetected,
                "blue.isCalculated": isBlueDetected,
                "yellow.isCalculated": isYellowDetected,
            }

            cursor= self.mongo_connection.objects.balls.find(values)

            # make directory if it doesn't exist
            if not os.path.exists(VIDEO_NEW_PATH):
                os.makedirs(VIDEO_NEW_PATH)

            for result_object in cursor:

                try:
                    num= int(str_n)+1
                    str_n = str(num)
                    str_n = str_n + ".jpg"
                    self.s3.Bucket(self.s3_bucket_name).download_file(result_object["frame0"], (VIDEO_NEW_PATH + str_n))
                    str_n = str_n.replace(".jpg","")
                    print("Downloading "+str_n+".jpg")

                except botocore.exceptions.ClientError as e:

                    if e.response['Error']['Code'] == "404":
                        print("The object does not exist.")
                    else:
                        raise

                    _frame_0.append((result_object["frame0"]))

                    red_x_points.append((result_object["red"]["x"]))
                    red_y_points.append((result_object["red"]["y"]))
                    red_z_points.append((result_object["red"]["z"]))

                    green_x_points.append((result_object["green"]["x"]))
                    green_y_points.append((result_object["green"]["y"]))
                    green_z_points.append((result_object["green"]["z"]))

                    blue_x_points.append((result_object["blue"]["x"]))
                    blue_y_points.append((result_object["blue"]["y"]))
                    blue_z_points.append((result_object["blue"]["z"]))

                    yellow_x_points.append((result_object["yellow"]["x"]))
                    yellow_y_points.append((result_object["yellow"]["y"]))
                    yellow_z_points.append((result_object["yellow"]["z"]))


            _global_points_red['x'] = red_x_points
            _global_points_red['y'] = red_y_points
            _global_points_red['y'] = red_z_points

            _global_points_green['x'] = green_x_points
            _global_points_green['y'] = green_y_points
            _global_points_green['z'] = green_y_points

            _global_points_blue['x'] = blue_x_points
            _global_points_blue['y'] = blue_y_points
            _global_points_blue['z'] = blue_z_points

            _global_points_yellow['x'] = yellow_x_points
            _global_points_yellow['y'] = yellow_y_points
            _global_points_yellow['z'] = yellow_z_points

            _frame_0_key['key'] = _frame_0

            self.create_video(videoName)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)



    def create_video(self, videoName):
        img_array = []
        for filename in glob.glob((VIDEO_NEW_PATH + '*.jpg')):
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)

        out = cv2.VideoWriter(VIDEO_PATH + videoName + '.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)

        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()
        print("Video Creation Completed")

        try:
            shutil.rmtree(VIDEO_NEW_PATH, ignore_errors=True)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        # def s3_get(self,key):
        #     try:
        #            #print(key)
        #              global str_n
        #
        #              num= int(str_n)+1
        #              str_n = str(num)
        #              str_n = str_n + '.jpg'
        #              self.s3.Bucket(self.s3_bucket_name).download_file(key, str_n)
        #              str_n.replace(".jpg","")
        #              print(str_n)
        #
        #     except botocore.exceptions.ClientError as e:
        #
        #             if e.response['Error']['Code'] == "404":
        #              print("The object does not exist.")
        #             else:
        #                 raise
