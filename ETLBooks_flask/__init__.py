from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

bycrypt = Bcrypt(app)

login_manager = LoginManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

app.config ["SECRET_KEY"] = "b269b45688f5a5fd3408a8ddf9b147a7"

db = SQLAlchemy(app)

login_manager.login_view = "login"

login_manager.login_message_category = "info"

from ETLBooks_flask import routes