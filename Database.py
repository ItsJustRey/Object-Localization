import pymongo
from pprint import pprint
import sys, os
import boto3
import cv2


class Database:
    def __init__(self):
        # MongoDB connection
        self.mongo_uri = "mongodb://icy_admin:Scrollaz2019!@icy0-shard-00-00-bkuxh.mongodb.net:27017,icy0-shard-00-01-bkuxh.mongodb.net:27017,icy0-shard-00-02-bkuxh.mongodb.net:27017/test?ssl=true&replicaSet=ICY0-shard-0&authSource=admin&retryWrites=true"
        self.mongo_connection = None

        # Amazon AWS S3 connection
        self.s3_access_key_id = ""
        self.s3_secret_access_key = ""
        self.s3_bucket_name = "icy-objects"
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
            frame0_key = "%s_%s_%s%s" % ("V0", date, time, ".jpg")
            frame1_key = "%s_%s_%s%s" % ("V1", date, time, ".jpg")
            frame2_key = "%s_%s_%s%s" % ("V2", date, time, ".jpg")

            # MongoDB Document Info
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
            # Insert object into MongoDB Cluster
            inserted_ball = self.mongo_connection.objects.balls.insert_one(values)
            print("Inserted " + str(values) + " with _id: " + str(inserted_ball.inserted_id))

            # Save frame0 to "test.jpg"
            cv2.imwrite("test0.jpg", frame0)
            #cv2.imwrite("test1.jpg", frame1)
            #cv2.imwrite("test2.jpg", frame2)

            # Open "test.jpg" and Insert object into Amazon S3 Bucket
            with open("test0.jpg", 'rb') as image:
                self.s3.Bucket(self.s3_bucket_name).put_object(Key = frame0_key , Body = image)
            # with open("test1.jpg", 'rb') as image:
            #     self.s3.Bucket(self.s3_bucket_name).put_object(Key=frame1_key, Body=image)
            # with open("test2.jpg", 'rb') as image:
            #     self.s3.Bucket(self.s3_bucket_name).put_object(Key=frame2_key, Body=image)

            #os.remove("test.jpg")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

    def get(self, getRed, getGreen, getBlue, getYellow):

        """ Get objects from database """
        try:
            query = {
                "date": "2019-02-28",
                "red.isCalculated": False,
                "green.isCalculated": False,
                "blue.isCalculated": True,
                "yellow.isCalculated": False
            }

            objects = self.mongo_connection.objects.balls.find(query)
            for obj in objects:
                print(obj)
                print(obj["frame0"])

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)