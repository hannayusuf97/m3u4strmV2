import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
import motor.motor_asyncio

# Load environment variables from a .env file
load_dotenv(find_dotenv())

# Get the MongoDB password from the environment variables
password = os.environ.get('MONGODB_PWD')
uri = os.environ.get('MONGODB_URI')
username = os.environ.get('MONGODB_USERNAME')
# Define the connection string with the provided credentials and IP address
connection_string = f"mongodb+srv://{username}:{password}@{uri}/?retryWrites=true&w=majority"

# Create a MongoClient to the running MongoDB instance
client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)

m3u4strm_db = client['m3u4strm']
movies_collection = m3u4strm_db['movies']
series_collection = m3u4strm_db['series']