import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector #this is what lets scraper insert the scraped books directly into the database make sure u install
import json
from pymongo import MongoClient
import time

# URL to scrape
url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

books = soup.find_all('article', class_='product_pod')

book_data = []

for book in books[:15]:

    # extract title
    title = book.h3.a['title']
    
    # extract price and drop pound sign
    price = book.find('p', class_='price_color').text.strip('£')

    # extract rating and convert to a number
    rating_class = book.find('p', class_='star-rating')['class'][1]
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    rating = rating_map.get(rating_class, 0)

    # extract author
    author_tag = book.find('p', class_='author')
    if author_tag and author_tag.text.strip():
        author = author_tag.text.strip()
    else:
        author = "Various Authors" # fall back on default value if there is no author

    # extract year
    year_tag = book.find('p', class_='year')
    if year_tag and year_tag.text.strip().isdigit():
        year = int(year_tag.text.strip())
    else:
        year = 2026 # fall back on default value if there is no year

    book_data.append({
        'Title': title,
        'Author': author,
        'Year': year,
        'Rating': rating,
        'Price': float(price)
    })

df = pd.DataFrame(book_data)
df.to_csv('data/techreads_books.csv', index=False)

# Connect to the database and insert the scraped data
# Make sure XAMPP is running and techreads_books.sql has been imported first (everyone has to import sql file individually)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="techreads_db" #woops
)
cursor = conn.cursor()

# extract and insert unique authors
unique_authors = df['Author'].unique()

author_id_map = {}

for author in unique_authors:
    cursor.execute(
        "INSERT INTO Authors (AuthorName) VALUES (%s)",
        (author,)
    )
    author_id = cursor.lastrowid
    author_id_map[author] = author_id

# insert books into table with mapped author IDs
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Books (Title, AuthorID, Year, Price, Rating)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        row['Title'],
        author_id_map[row['Author']],   # dynamically mapped ID
        row['Year'],
        float(row['Price']),
        row['Rating']
    ))

conn.commit()
cursor.close()
conn.close()

# task 4 mongodb insertion and queries

# Load CSV
df = pd.read_csv("data/techreads_books.csv")

json_file_path = "techreads_books.json"

df.to_json(json_file_path, orient="records", indent=4)

print("CSV successfully converted to JSON.")

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://eringoonan:dbengineering@cluster0.9ib8exk.mongodb.net/?appName=Cluster0")

db = client["techreads_db"]
collection = db["books"]

# Clear collection to avoid duplicates
collection.delete_many({})

# Load JSON file
with open(json_file_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

# Insert into MongoDB
start_time = time.time()
collection.insert_many(json_data)
end_time = time.time()

print("Data inserted into MongoDB successfully.")
print("Insertion time:", end_time - start_time, "seconds")

# mongo db query testing section

start = time.time()

mongo_q1 = list(
    collection
    .find({}, {"_id": 0, "Title": 1, "Year": 1, "Price": 1})
    .sort("Price", 1)
)

mongo_time_q1 = time.time() - start

start = time.time()

mongo_q2 = list(
    collection
    .find({}, {"_id": 0, "Title": 1, "Author": 1, "Rating": 1})
    .sort("Rating", -1)
)

mongo_time_q2 = time.time() - start

print("MongoDB Query 2 time:", mongo_time_q2)

print("MongoDB Query 1 time:", mongo_time_q1)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="techreads_db"
)

cursor = conn.cursor()

# sql query testing section

# Query 1: Title, Year, Price ordered by Price ASC
start = time.time()
cursor.execute("""
    SELECT Title, Year, Price
    FROM Books
    ORDER BY Price ASC;
""")
query1_result = cursor.fetchall()
mysql_time_q1 = time.time() - start


# Query 2: Title, Author, Rating ordered by Rating DESC
start = time.time()
cursor.execute("""
    SELECT Books.Title, Authors.AuthorName, Books.Rating
    FROM Books
    INNER JOIN Authors 
        ON Books.AuthorID = Authors.AuthorID
    ORDER BY Books.Rating DESC;
""")
query2_result = cursor.fetchall()
mysql_time_q2 = time.time() - start

print("MySQL Query 1 time:", mysql_time_q1)
print("MySQL Query 2 time:", mysql_time_q2)

cursor.close()
conn.close()