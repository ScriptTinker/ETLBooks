from flask import render_template,url_for,flash,redirect,request,jsonify, session
from ETLBooks_flask.models import User,Book,Progress
from ETLBooks_flask.forms import RegistrationForm, LoginForm, UpdateAccountForm
from ETLBooks_flask import app,db,bycrypt
from flask_login import login_user,current_user,logout_user,login_required
from web_scraper import web_scraper
from book_counter import book_counter
from plotly_graphs import dash_app


@app.route("/")
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if user and bycrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember= form.remember.data)
            next_page = request.args.get("next")
            flash("You've been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Logging failed! Try again!", "danger")

    return render_template("login.html", title= "Login", form=form)

"""
^^^^^^^^^^^^^^^^^^^^^^^^
This is just a demo to implement a logging system with certain roles where the admin can
access all the features while operators could only add books,remove etc...
There is a version without logging for easier access
The email and password for the main admin would be admin@test.com and admin respectively

REMEMBER THAT YOU JUST REWRITE THE CODE TO DEBUG IT 
YOU REMOVED LOGINGS,TEMPLATES AND MUST ADD A WAY TO UPDATE THE IFRAMES OF THE DATA IN A DYNAMIC WAY!!!!
YOU MUST CREATE A SESSION THAT KEEPS TRACK OF TOTAL BOOKS AND DEVIDE THEM BY PROCESS BOOK FOR THE LOADING BAR!
YOU MUST LEARN JS YOU FUCKING IDIOT
"""

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/home")
def home():
    page = request.args.get("page", type=int)
    books = Book.query.paginate(page=page,per_page=10)
    return render_template("home.html", title= "Homepage", page = page, books=books)


@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template("register.html",form = form)

@app.route("/scraper")
def scraper():
    total_books = session.get("total_books", 0)
    return render_template("scraper.html", total_books=total_books)


@app.route("/scraper/prepare_scraper")
def prepare_scraper():
    #user_id = current_user.id
    total_books = book_counter()
    
    existing_progress = Progress.query.first()
    #existing_progress = Progress.query.filter_by(user_id=user_id).first()

    if existing_progress:
        existing_progress.total_books = total_books
        existing_progress.processed_books = 0
        existing_progress.cancelled = False
    else:
        new_progress = Progress(total_books=total_books, processed_books=0)
        #new_progress = Progress(total_books=total_books, processed_books=0, user_id=user_id)
        db.session.add(new_progress)

    db.session.commit()        

    return jsonify({"success": True, "total_books": total_books})

@app.route("/scraper/start_scraper")
def start_scraper():  
    web_scraper()
    return jsonify({"success": True})

@app.route("/scraper/get_progress")
def get_progress():
    #user_id=current_user.id
    #progress = Progress.query.filter_by(user_id=user_id).first()
    progress = Progress.query.first()
    total_books = progress.total_books
    processed_books = progress.processed_books

    print(f"Total Books: {total_books}, Processed Books: {processed_books}")
    
    if total_books > 0:
        progress = (processed_books / total_books) * 100
    else:
        progress = 0
    
    return jsonify({"progress": progress})

@app.route("/scraper/cancel_scraping", methods=["POST", "GET"])
def cancel_scraping():
    #user_id= current_user.id
    #cancel=Progress.query.filter_by(user_id=user_id).first()
    cancel = Progress.query.first()
    if cancel:
        cancel.cancelled = True
    db.session.commit()

    return jsonify({"success": True})

@app.route("/book/<int:book_id>")
def books():
    pass

@app.route("/book/new")
def new_book():
    pass

@app.route("/book/delete")
def delete_book():
    pass

@app.route("/analyse/")
def analyse():
    return render_template("analyse.html")
