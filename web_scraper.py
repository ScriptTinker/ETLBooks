import requests
from bs4 import BeautifulSoup
from ETLBooks_flask.models import Book,Progress
from ETLBooks_flask import app,db
from io import BytesIO
from urllib.parse import urljoin

def checkPagination(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    next_button = soup.find("li", class_="next")
    return next_button is not None
"""
^^^^^^^^^^^
A simple check to see if the next button exists
If it does, dive into the next page and extract data
Otherwise retrun false and continue to next category
"""


def web_scraper():
    with app.app_context(): 
        base_url = "https://books.toscrape.com"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, "lxml")
        i = 2  # Start at page 2 for pagination
        progress = Progress.query.first()
        #user_id=current_user.id
        #progress = Progress.query.filter_by(user_id=user_id).first()


        ol = soup.find("div", class_="side_categories")
        categories = list(ol.stripped_strings)
        categories.remove("Books")  # Remove "Books" as it's not a category
        """
        ^^^^^^^^^^^^
        This makes the categories readble for the program
        It acts as a .strip() fuction, however the later 
        also includes whitespace in the list
        """
        for category in categories:  
            try:
                url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(" ", "-")}_{i}/index.html"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "lxml")
                pagecount = 2  # Reset page count for each category

                books = soup.find_all("article", class_="product_pod")


                for book in books:
                    name = book.h3.a["title"]
                    price = book.find("p", class_="price_color").text[1:]  # Remove £ symbol
                    review = book.find("p", class_="star-rating")["class"][1]  # Star rating

                    image_tag = book.find("img", class_="thumbnail")
                    image_url = urljoin(base_url, image_tag["src"])  # Making the image URL absolute

                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image = BytesIO(image_response.content).read()  # Read as binary
                    else:
                        image = None

                    book_dive_url = "https://books.toscrape.com/catalogue" + book.h3.a["href"].replace("../../../","/")
                    # Now we dive into each book for aditional data.                                 ^^^ This clears the previous path of the href(see webiste for reference)
                    response = requests.get(book_dive_url)
                    soup = BeautifulSoup(response.text, "lxml")

                    availability_text = soup.find("p", class_="instock availability").text.strip()

                    if "in stock" in availability_text.lower():
                        availability = True
                        stock_text = availability_text.split()[-2]
                        stock = int(stock_text.strip("("))
                    else:
                        availability = False
                        stock = 0

                    # Insert book data into the database using SQLAlchemy
                    new_book = Book(name=name,
                                    price=float(price.replace("£", "")),
                                    review=review, 
                                    category=category , 
                                    availability = availability, 
                                    stock = stock,
                                    image=image)
                    
                    progress.processed_books += 1
                    db.session.add(new_book)
                    db.session.commit()

                    if progress.cancelled:
                        return

                while checkPagination(url):
                    url = f"https://books.toscrape.com/catalogue/category/books/{category.lower().replace(" ", "-")}_{i}/page-{pagecount}.html"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, "lxml")
                    pagecount += 1

                    books = soup.find_all("article", class_="product_pod")

                    for book in books:
                        name = book.h3.a["title"]
                        price = book.find("p", class_="price_color").text[1:]
                        review = book.find("p", class_="star-rating")["class"][1]

                        image_tag = book.find("img", class_="thumbnail")
                        image_url = urljoin(base_url, image_tag["src"])  # Making the image URL absolute

                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            image = BytesIO(image_response.content).read()  # Read as binary
                        else:
                            image = None

                        book_dive_url = "https://books.toscrape.com/catalogue" + book.h3.a["href"].replace("../../../","/")
                        # Now we dive into each book for aditional data.                                 ^^^ This clears the previous path of the href(see webiste for reference)
                        response = requests.get(book_dive_url)
                        soup = BeautifulSoup(response.text, "lxml")

                        availability_text = soup.find("p", class_="instock availability").text.strip()

                        if "in stock" in availability_text.lower():
                            availability = True
                            stock_text = availability_text.split()[-2]
                            stock = int(stock_text.strip("("))#Without strip() we have a string like this one: "(19"
                        else:
                            availability = False
                            stock = 0

                    # Insert book data into the database using SQLAlchemy
                        new_book = Book(name=name,
                                price=float(price.replace("£", "")),
                                review=review,
                                category=category, 
                                availability = availability, 
                                stock = stock,
                                image=image)
                        
                        progress.processed_books += 1
                        db.session.add(new_book)
                        db.session.commit()

                        if progress.cancelled:
                            return

            except Exception as e:
                print(f"Error at {e}")

            print(f"The books from the {category} category are loaded!")
            i += 1

        # Commit the changes to the database
        db.session.commit()

if __name__ == "__main__":
    web_scraper()