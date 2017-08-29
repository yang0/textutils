
from pymongo import MongoClient

class MongoUtil():

    def __init__(self, dbName, collectionName, host='localhost', port=27017):
        self.client = MongoClient(host, port)
        db = self.client[dbName]
        self.collection = db[collectionName]


    def insert(self, key, value):
        obj = {"KeyName": key, "KeyValue": value}

        self.collection.insert_one(obj)