import pymongo
from pprint import pprint
import sys, os
import boto3
import gridfs
import cv2

from bson import Binary
from PIL import Image


class Database:
    def __init__(self):

        # MongoDB connection
        self.mongo_uri = "mongodb://icy_admin:Scrollaz2019!@icy0-shard-00-00-bkuxh.mongodb.net:27017,icy0-shard-00-01-bkuxh.mongodb.net:27017,icy0-shard-00-02-bkuxh.mongodb.net:27017/test?ssl=true&replicaSet=ICY0-shard-0&authSource=admin&retryWrites=true"
        self.mongo_connection = None

        # Amazon AWS S3 connection
        self.s3_access_key_id = "AKIAJMJWXVM4HWJ3M7JA"
        self.s3_secret_access_key = "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"
        self.s3_bucket_name = "icy-objects"
        self.s3 = None
        # self.s3_connection = None

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
            image = open("Videos/icy.jpg", 'rb')
            self.s3.Bucket(self.s3_bucket_name).put_object(Key = "icy_test1.jpg", Body = image)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

    def insert(self, date, time, frame0, frame1, frame2, red, green, blue, yellow):
        """ Insert data into database """
        try:
            # CREATE KEY FOR EACH FRAME/IMAGE
            frame0_key = "%s_%s_%s" % ("V0", date, time)
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

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

    7
