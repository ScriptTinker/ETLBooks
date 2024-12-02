from flask import render_template,url_for,flash,redirect,request, abort
from ETLBooks_flask.models import User,Post
from ETLBooks_flask.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from ETLBooks_flask import app,db,bycrypt
from flask_login import login_user,current_user,logout_user,login_required
from PIL import Image
import secrets
import os




@app.route("/")
@app.route("/home")
def home():
    pass

@app.route("/blog")
def about():
    return render_template("about.html",title = "about")

@app.route("/register/blog", methods = ["POST", "GET"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bycrypt.generate_password_hash(form.password.data).decode("UTF-8")
        user = User(username=form.username.data, email=form.email.data,password=hashed_password )
        db.session.add(user)
        db.session.commit()

        flash(f"Your account has been created!You can now log in!", "success")
        return redirect(url_for("home"))
        
    return render_template("Register.html", title= "Register", form=form)

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
    return redirect(url_for("blog"))

def delete_old_pic(filename):
    file_path = os.path.join(app.root_path, "static/profile_pics", filename)
    if os.path.exists(file_path):
        os.remove(file_path)

def save_picture(form_picture):
    try:
        random_hex = secrets.token_hex(8)
        _ , f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

        output_size= (250, 300)
        i= Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)

        return picture_fn
    except Exception as e:
        flash(e,"danger")
    
@app.route("/blog/account",methods =["POST","GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit(): 
        if form.picture.data:
            delete_old_pic(current_user.image)
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file #<<<remember to have uniform name 
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("your account has been updated!", "success")
        return redirect(url_for("account"))
    
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for("static", filename=f"profile_pics/{current_user.image}")
    return render_template("account.html", title="Account",
                            image_file=image_file, form = form)


@app.route("/post/new", methods=["GET","POST"])
@login_required
def new():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title= form.title.data, content= form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!","success")
        return redirect(url_for("home"))
    return render_template("create_post.html", title = "New post", form = form,
                           legend = "New post")


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title= post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=["POST", "GET"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title = "Update post", form = form,
                           legend = "Update Post")    
    
@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
     
     post = Post.query.get_or_404(post_id)
     if post.author != current_user:
        abort(403)
     db.session.delete(post)
     db.session.commit()
     flash("Your post has been deleted!", "success")
     return redirect(url_for("home"))    