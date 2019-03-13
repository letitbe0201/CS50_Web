# CS50 Web ### Python, JavaScript, SQL
### Project 1

#### Implementing a book review website.

###### Users could be able to
* Register and log in their account
* Search for books by ISBN, author name, book title, etc
* Get information of the book as well as average rating and count of ratings from [Goodreads](https://www.goodreads.com/)
* Leave a rating and review, also see others' reviews in each book page

###### Files include
* _application.py_ Using FLASK to control the htmls and determine how to interact with the user's requests
* _helpers.py_ two function: 1. Render a apology image from [memegen](https://github.com/jacebrowning/memegen#special-characters) 2. Decorate routes to require login
* _import.py_ Import the csv file of book information provided by CS50
* _index.html_ Index page, the user could type in any words to search for a book
* _login.html_ _register.html_ Let the user log in the website or register an account
* _book.html_ List the searching result and link to every book display on the page
* _result.html_ Show the information of the book (title, author, publication year, etc), and all the ratings, reviews left by users