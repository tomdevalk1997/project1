# project1

This project contains a website to read and write book reviews.

import.py contains the Python script to import data from books.csv and stores the data in a Heroku database
refresh_ratings.py contains the Python script to obtain the ratings from goodreads for all of the books in the database
application.py contains the flask application that connects the different pages of the website

index.html contains the homepage of the website. This page contains a global description on how the website works and a list of the top 10 rated books in Goodreads.
books.html contains a search field as well as a list of the top 10 rated books in Goodreads. This page is also used to display search results. (login required)
book.html contains the information regarding a selected book as well as a list of the top 10 rated books in Goodreads. (login required)
register.html contains a form to create an account. This enables the user to search and access book pages.
layout.html contains the global layout for all of the html pages.
styles.scss / styles.css contains the stylesheet for the html pages

All of the necessary Python packages:
  os
  flask - Flask, session, url_for, render_template, redirect, request
  flask_session - Session
  sqlalchemy - create_engine
  sqlalchemy.orm - scoped_session, sessionmaker
  requests
  json
  datetime
