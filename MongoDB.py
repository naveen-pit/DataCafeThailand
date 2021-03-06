import pymongo
from pymongo import MongoClient
class MongoDBManager:
    def __init__(self,database,server = 'localhost',port=27017):
        self.client = MongoClient(server,port)
        self.db = self.client[database]
    def insert_one(self,collection,data):
        collection = self.db[collection]
        collection.insert_one(data)
    def insert_many(self,collection,data):
        collection = self.db[collection]
        collection.insert_many(data)
    def get_all_from_collection(self,collection):
        collection = self.db[collection]
        data=[]
        results= collection.find({})
        for result in results:
            data.append(result)
        return data
if __name__=="__main__":
    mongo = MongoDBManager('PageCollab')
    mongo.insert_one('test',{'test':1})