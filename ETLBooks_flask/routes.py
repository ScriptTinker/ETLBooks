from flask import render_template,url_for,flash,redirect,request,jsonify, session
from ETLBooks_flask.models import User,Book,Progress
from ETLBooks_flask.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, BookForm
from ETLBooks_flask import app,db,bycrypt,mail
from flask_mail import Message
from flask_login import login_user,current_user,logout_user,login_required
from web_scraper import web_scraper
from book_counter import book_counter
from plotly_graphs import composition_thumbnail


@app.route("/", methods = ["GET", "POST"])
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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

@app.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bycrypt.generate_password_hash(form.password.data).decode("UTF-8")
        user = User(name=form.name.data, email=form.email.data,password=hashed_password )
        db.session.add(user)
        db.session.commit()

        flash(f"Your account has been created!You can now log in!", "success")
        return redirect(url_for("login"))
        
    return render_template("Register.html", title= "Register", form=form)

"""
^^^^^^^^^^^^^^^^^^^^^^^^
This is just a demo to implement a logging system with certain roles where the admin can
access all the features while operators could only add books,remove etc...
There is a version without logging for easier access
The email and password for the main admin would be admin@test.com and admin respectively
"""

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/profile")
def profile():
    form = UpdateAccountForm()
    return render_template("profile.html", form=form)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/scraper")
def scraper():
    return render_template("scraper.html")

@app.route("/scraper/prepare_scraper", methods=["POST","GET"])
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


@app.route("/overview")
def overview():
    page = request.args.get("page", type=int)
    books = Book.query.paginate(page=page,per_page=10)
    return render_template("overview.html", title= "Overview", page = page, books=books)

@app.route("/book/<int:book_id>")
def books():
    pass

@app.route("/book/new")
def new_book():
    form = BookForm()
    return render_template("new_book.html",form=form, title= "Add Book")

@app.route("/book/delete")
def delete_book():
    pass

@app.route("/analyse")
def analyse():
    return render_template("analyse.html", title="Data Analysis",composition_thumbnail=composition_thumbnail)

@app.route("/analyse/pie_chart")
def pie_chart():
    return render_template("pie_chart.html", title = "Book Composition")

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", 
                  sender="noreply@demo.com",
                  recipients=[user.email])
    msg.body=f'''
To reset your password, visit the following link:
{url_for("reset_token", token=token, _external=True)}
If you feel like this is a mistake, just ignore this email!
'''
    mail.send(msg)
    
@app.route("/reset_password", methods=["GET","POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash("An email was sent to the email you type in, please check your email")
    return render_template("reset_request.html", title = "Reset Password", form=form)

@app.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(home)
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token!", "warning")
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm
    if form.validate_on_submit():
        hashed_password = bycrypt.generate_password_hash(form.password.data).decode("UTF-8")
        user.password = hashed_password
        db.session.commit()
    return render_template('reset_password.html', title = "Reset Password", form = form)
