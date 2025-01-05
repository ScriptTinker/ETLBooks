from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)

bycrypt = Bcrypt(app)

login_manager = LoginManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ETLbook.db"

app.config ["SECRET_KEY"] = "secret_key"

app.config['DEBUG'] = True

app.config["MAIL_SERVER"] = "smtp.googlemail.com"

app.config["MAIL_PORT"] = 587

app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")

app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

mail = Mail(app)

db = SQLAlchemy(app)

login_manager.login_view = "login"

login_manager.login_message_category = "info"

from ETLBooks_flask.models import User,Book,Progress
with app.app_context():
    if not os.path.exists('/istance/ETLbook.db'):
        db.create_all()

from ETLBooks_flask import routes        
