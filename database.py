import pymongo
from pymongo import MongoClient
import dotenv, os

dotenv.load_dotenv()

secret_key = os.environ.get("SECRET_KEY")

client = MongoClient('localhost', 27017)
db = client['chipotleapi']