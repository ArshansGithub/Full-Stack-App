import pymongo
from pymongo import MongoClient

secret_key = "asdsagasdsadsadsadghasdsad3"

client = MongoClient('localhost', 27017)
db = client['chipotleapi']