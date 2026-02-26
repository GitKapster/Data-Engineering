-- this is just used for importing, i think everyone has to bootup phpmyadmin to import this database
-- Scraper.py should be inserts the contents of scraped data into the database

CREATE DATABASE IF NOT EXISTS techreads_db;
USE techreads_db;

-- Authors Info
CREATE TABLE IF NOT EXISTS Authors (
  AuthorID int PRIMARY KEY AUTO_INCREMENT,
  AuthorName varchar(255)
);

-- Books Info
CREATE TABLE IF NOT EXISTS Books (
  BookID int PRIMARY KEY AUTO_INCREMENT,
  Title varchar(255) NOT NULL,
  AuthorID int,
  Year int,
  Price DECIMAL(6,2),
  Rating int,
  FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)
);

-- query to extract title, year and price, ordered by price
SELECT Title, Year, Price
FROM Books
ORDER BY Price ASC;

-- query to extract books, author, rating ordered by rating
SELECT Books.Title, Authors.AuthorName, Books.Rating
FROM Books
INNER JOIN Authors 
ON Books.AuthorID = Authors.AuthorID
ORDER BY Books.Rating DESC;
