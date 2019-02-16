import pymongo
from pprint import pprint
import sys, os



class Database:
    def __init__(self):
        self.uri = "mongodb://icy_admin:Scrollaz2019!@icy0-shard-00-00-bkuxh.mongodb.net:27017,icy0-shard-00-01-bkuxh.mongodb.net:27017,icy0-shard-00-02-bkuxh.mongodb.net:27017/test?ssl=true&replicaSet=ICY0-shard-0&authSource=admin&retryWrites=true"
        self.connection = None

    def connect(self):
        """ Connect to database """
        try:
            self.connection = pymongo.MongoClient(self.uri)
            # Issue the serverStatus command and print the results
            serverStatusResult= self.connection.admin.command("serverStatus")
            pprint(serverStatusResult)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)


    def insert(self, date, time, red, green, blue, yellow):
        """ Insert data into database """
        try:
            values = {
                'date':     date,
                'time':     time,
                'red':      red,
                'green':    green,
                'blue':     blue,
                'yellow':   yellow,
            }
            inserted_ball = self.connection.objects.balls.insert_one(values)
            print("Inserted " + str(values) + " with _id: " + str(inserted_ball.inserted_id))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
    7

