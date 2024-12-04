from datetime import datetime
from __init__ import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True) 
    image = db.Column(db.String(20), nullable=False, default = "default.jpg")
    password = db.Column(db.String(60), nullable=False)  #^^^ remeber to have uniform names!!!

    def __repr__(self):
        return f"User:'{self.username}','{self.email}''{self.image}'"
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    price = db.Column(db.Float, nullable = False)
    review = db.Column(db.String(50), nullable = False)
    category = db.Column(db.String(255), nullable = False)
    avalability = db.Column(db.Boolean, nullable = False)
    stock = db.Column(db.Integer)

    def __repr__(self):
        return f'<Book {self.name}, {self.category},{self.price}>'