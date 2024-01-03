import pymongo
from pymongo import MongoClient

secret_key = "top secret key"

client = MongoClient('localhost', 27017)
db = client['chipotleapi']