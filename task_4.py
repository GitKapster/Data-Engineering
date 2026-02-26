#Task 4 MongoDB Integration & Performance Comparison
#Import required libraries
import pandas as pd
import json
from pymongo import MongoClient
import time
import mysql.connector

#Load CSV and convert to JSON
df = pd.read_csv("data/Scraped_Data.csv") #From line 45 of scraper.py
df.to_json("Scraped_Data.json", orient="records", indent=4) #Converted to .json

#Insert JSON into MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["scraped_data"] #Changed the name because it was different than our database name
collection = db["books"]

with open("Scraped_Data.json") as f:
    data = json.load(f)

collection.drop() #Added this so that we dont insert duplicates
collection.insert_many(data)

#MongoDB queries
start = time.time()
mongo_result = list(collection.find({"Price": {"$lt": 40}}))
mongo_time = time.time() - start

#MySQL comparison
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="scraped_data"
)
cursor = conn.cursor()

start = time.time()
cursor.execute("SELECT * FROM Books WHERE Price < 40;")
mysql_result = cursor.fetchall()
mysql_time = time.time() - start

print("MongoDB time:", mongo_time) #Show the time on MongoDB query
print("MySQL time:", mysql_time) #Show the time on MySQL query
