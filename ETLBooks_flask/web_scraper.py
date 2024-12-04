import requests
from bs4 import BeautifulSoup
from models import Book
from __init__ import app,db


def web_scraper():
    def checkPagination(): 
        # A simple check to see if there is the "next" button
        btn = soup.find("li", class_="next")
        if not btn:
            return False
        else:
            return True

    with app.app_context():  # Use Flask's app context for accessing db
        url = "https://books.toscrape.com"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        i = 2  # Start at page 2 for pagination

        ol = soup.find("div", class_="side_categories")
        categories = list(ol.stripped_strings)
        categories.remove("Books")  # Remove "Books" as it's not a category

        for category in categories:  
            try:
                url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(' ', '-')}_{i}/index.html"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "lxml")
                pagecount = 2  # Reset page count for each category

                books = soup.find_all('article', class_='product_pod')

                for book in books:
                    name = book.h3.a['title']
                    price = book.find('p', class_='price_color').text[1:]  # Remove £ symbol
                    review = book.find('p', class_='star-rating')['class'][1]  # Star rating
                    

                    book_dive_url = "https://books.toscrape.com/catalogue" + book.h3.a["href"].replace("../../../","/")
                    # Now we dive into each book for aditional data.                                 ^^^ This clears the previous path of the href
                    response = requests.get(book_dive_url)
                    soup = BeautifulSoup(response.text, "lxml")

                    availability_text = soup.find("p", class_="instock availability").text.strip()

                    if "in stock" in availability_text.lower():
                        avalability = True
                        stock_text = availability_text.split()[-2]
                        stock = int(stock_text.strip("("))
                    else:
                        avalability = False
                        stock = 0

                    # Insert book data into the database using SQLAlchemy
                    new_book = Book(name=name, price=float(price.replace("£", "")), review=review, category=category , avalability = avalability, stock = stock)
                    db.session.add(new_book)

                while checkPagination():
                    url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(' ', '-')}_{i}/page-{pagecount}.html"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, "lxml")
                    pagecount += 1

                    books = soup.find_all('article', class_='product_pod')

                    for book in books:
                        name = book.h3.a['title']
                        price = book.find('p', class_='price_color').text[1:]
                        review = book.find('p', class_='star-rating')['class'][1]

                        if "in stock" in availability_text.lower():
                            avalability = True
                            stock_text = availability_text.split()[-2]
                            stock = int(stock_text.strip("("))
                        else:
                            avalability = False
                            stock = 0

                    # Insert book data into the database using SQLAlchemy
                    new_book = Book(name=name, price=float(price.replace("£", "")), review=review, category=category , avalability = avalability, stock = stock)
                    db.session.add(new_book)

            except Exception as e:
                print(f"Error at {e}")

            print(f"The books from the {category} category are loaded!")
            i += 1

        # Commit the changes to the database
        db.session.commit()

if __name__ == "__main__":
    web_scraper()