from flask import session
import requests
from bs4 import BeautifulSoup
from ETLBooks_flask import app

def checkPagination(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    next_button = soup.find("li", class_="next")
    return next_button is not None

def book_counter():
    base_url = "https://books.toscrape.com"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "lxml")

    ol = soup.find("div", class_="side_categories")
    categories = list(ol.stripped_strings)
    categories.remove("Books")  # Remove "Books" as it's not a category
    """
        ^^^^^^^^^^^^
        This makes the categories readble for the program
        It acts as a .strip() fuction, however the later 
        also includes whitespace in the list
    """

    total_books: int = 0
    i = 2 #this is for pagination control
    with app.app_context():
        for category in categories:
            try:
                url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(" ", "-")}_{i}/index.html"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "lxml")
                pagecount = 2

                books = books = soup.find_all("article", class_="product_pod")

                    
                total_books = total_books + len(books)
                session["total_books"] = total_books

                while checkPagination(url):

                    url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(" ", "-")}_{i}/page-{pagecount}.html"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, "lxml")
                    pagecount += 1

                    books = soup.find_all("article", class_="product_pod")

                    total_books = total_books + len(books)
                    session["total_books"] = total_books

                i += 1
            except Exception as e:
                pass    

    return total_books