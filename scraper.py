import requests
from bs4 import BeautifulSoup
import pandas as pd

#Put a link here for whatever website you want to scrape
url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
print(f"Fetching: {url}")
response = requests.get(url)
print(f"Response status: {response.status_code}")

soup = BeautifulSoup(response.content, 'html.parser')

# Find all book containers
books = soup.find_all('article', class_='product_pod')
print(f"Found {len(books)} books")

# Store the data in a list
book_data = []

# Loop through each book and extract info
for book in books[:15]:  # Get first 15 books
    
    # Title
    title = book.h3.a['title']
    
    # Price (remove the £ symbol)
    price = book.find('p', class_='price_color').text.strip('£')
    
    # Rating (convert to numbers)
    rating_class = book.find('p', class_='star-rating')['class'][1]
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    rating = rating_map.get(rating_class, 0)
    
    # This site doesn't have author or year, so we'll add dummy data
    author = "Various Authors"
    year = 2024
    
    # Add to list
    book_data.append({
        'Title': title,
        'Author': author,
        'Year': year,
        'Rating': rating,
        'Price': float(price)
    })

print(f"Extracted {len(book_data)} books")

# Convert to DataFrame
df = pd.DataFrame(book_data)

# Save to CSV
df.to_csv('data/techreads_books.csv', index=False)
print("Saved to data/techreads_books.csv")

# Show what we got
print("\n", df)
print(f"\nScraped {len(df)} books successfully!")