from flask import render_template,url_for,flash,redirect,request
from models import User,Book
from forms import RegistrationForm, LoginForm, UpdateAccountForm
from ETLBooks_flask import app,db,bycrypt
from flask_login import login_user,current_user,logout_user,login_required
from PIL import Image
from web_scraper import web_scraper

@app.route("/")
@app.route("/login", methods = ["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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

    return render_template("Login.html", title= "Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@login_required
@app.route("/home")
def home():
    page = request.args.get("page", type=int)
    books = Book.query.paginate(page=page,per_page=10)
    pass

@login_required
@app.route("/book/<int:book_id>")
def books():
    pass

@login_required
@app.route("/book/new")
def books():
    pass

@login_required
@app.route("/home/scrape")
def scrape():
    web_scraper()

@login_required
@app.route("/analyse")
def analyse():
    pass