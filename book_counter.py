from flask import flash
import requests
from bs4 import BeautifulSoup
from ETLBooks_flask import app

def checkPagination(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    next_button = soup.find("li", class_="next")
    return next_button is not None

def retry_scrape(url):
    for i in range (1,3):    
        response = requests.get(url)
        if response.status_code == 200:
            return response
    flash("Error while trying to scrape!")        


def book_counter():
    base_url = "https://books.toscrape.com"
    response = requests.get(base_url)
    if response.status_code != 200:
        retry_scrape(base_url)
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
                url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(' ', '-')}_{i}/index.html"
                response = requests.get(url)
                if response != 200:
                    response.status_code = retry_scrape(url)
                soup = BeautifulSoup(response.text, "lxml")
                pagecount = 2

                books = books = soup.find_all("article", class_="product_pod")

                    
                total_books = total_books + len(books)

                while checkPagination(url):

                    url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(' ', '-')}_{i}/page-{pagecount}.html"
                    response = requests.get(url)
                    if response.status_code != 200:
                        response = retry_scrape(url)
                    soup = BeautifulSoup(response.text, "lxml")
                    pagecount += 1

                    books = soup.find_all("article", class_="product_pod")

                    total_books = total_books + len(books)

                i += 1
            except Exception as e:
                pass    

    return total_books