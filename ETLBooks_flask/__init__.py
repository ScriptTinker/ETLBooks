from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)

bycrypt = Bcrypt(app)

login_manager = LoginManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ETLbook.db"

app.config ["SECRET_KEY"] = ""

db = SQLAlchemy(app)

login_manager.login_view = "login"

login_manager.login_message_category = "info"

from ETLBooks_flask.models import User,Book
with app.app_context():
    if not os.path.exists('/istance/ETLbook.db'):
        db.create_all()
        