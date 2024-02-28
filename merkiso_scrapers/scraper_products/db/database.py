# lib
from pymongo import MongoClient


# scraper
from scraper_products.settings import MONGO_URI

class DbConnection:

    def __init__(self) -> None:
        self.client = MongoClient(MONGO_URI)

    def get_db(self, db_name: str):
        return self.client[db_name]
    
    def get_collection(self, db_name: str, collection_name: str):
        return self.get_db(db_name)[collection_name]
    
    def close(self):
        self.client.close()
    
    def create_index(self, db_name: str, collection_name: str, index: str):
        collection = self.get_collection(db_name, collection_name)
        collection.create_index(index, unique=True)
    
    def insert_one(self, db_name: str, collection_name: str, data: dict):
        collection = self.get_collection(db_name, collection_name)
        collection.insert_one(data)
        
    def insert_many(self, db_name: str, collection_name: str, data: list):
        collection = self.get_collection(db_name, collection_name)
        collection.insert_many(data)
        
    def find_one(self, db_name: str, collection_name: str, query: dict):
        collection = self.get_collection(db_name, collection_name)
        return collection.find_one(query)
    
    def find(self, db_name: str, collection_name: str, query: dict):
        collection = self.get_collection(db_name, collection_name)
        return collection.find(query)
    
    def update_one(self, db_name: str, collection_name: str, query: dict, data: dict):
        collection = self.get_collection(db_name, collection_name)
        collection.update_one(query, data, upsert=True)