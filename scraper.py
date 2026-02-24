import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector #this is what lets scraper insert the scraped books directly into the database make sure u install

# URL to scrape
url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all book containers
books = soup.find_all('article', class_='product_pod')

# Store the data in a list
book_data = []

# Loop through each book and extract info
for book in books[:15]:  # Get first 15 books

    # Title
    title = book.h3.a['title']

    # Price (remove the £ symbol)
    price = book.find('p', class_='price_color').text.strip('£')

    # Rating (convert stars to a number)
    rating_class = book.find('p', class_='star-rating')['class'][1]
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    rating = rating_map.get(rating_class, 0)

    # Site doesnt have author or year so we use placeholders (pray the teacher isnt mad but we can also fix by finding a new site)
    author = "Various Authors"
    year = 2024

    book_data.append({
        'Title': title,
        'Author': author,
        'Year': year,
        'Rating': rating,
        'Price': float(price)
    })

# Save to CSV
df = pd.DataFrame(book_data)
df.to_csv('data/Scraped_Data.csv', index=False)

# Connect to the database and insert the scraped data
# Make sure XAMPP is running and scraped_data.sql has been imported first (everyone has to import sql file individually)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="techreads_db"
)
cursor = conn.cursor()

# Insert placeholder author because books to scrape doesnt have authors and without this there is FK errors
cursor.execute("INSERT IGNORE INTO Authors (AuthorID, AuthorName) VALUES (1, 'Various Authors')")

# Clear old data so we dont get duplicates if run again
cursor.execute("DELETE FROM Books")

# Insert each book into the database
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Books (Title, AuthorID, Year, Price, Rating)
        VALUES (%s, %s, %s, %s, %s)
    """, (row['Title'], 1, row['Year'], float(row['Price']), row['Rating']))

conn.commit()
cursor.close()
conn.close()