import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector #this is what lets scraper insert the scraped books directly into the database make sure u install

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
df.to_csv('data/Scraped_Data.csv', index=False)

# Connect to the database and insert the scraped data
# Make sure XAMPP is running and scraped_data.sql has been imported first (everyone has to import sql file individually)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="scraped_data" #This had the wrong name as well changed it back to scraped data
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