CREATE DATABASE IF NOT EXISTS scraped_data;
USE scraped_data;

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