from datetime import datetime,date
from ETLBooks_flask import db, login_manager
from flask_login import UserMixin



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True) 
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="Operator")
                    

    def __repr__(self):
        return f"User:'{self.name}','{self.email}'"
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    price = db.Column(db.Float, nullable = False)
    review = db.Column(db.String(50), nullable = False)
    category = db.Column(db.String(255), nullable = False)
    availability = db.Column(db.Boolean, nullable = False)
    stock = db.Column(db.Integer)
    image = db.Column(db.LargeBinary)
    date_extracted = db.Column(db.Date, default=date.today , nullable=False)



    def __repr__(self):
        return f'<Book {self.name}, {self.category},{self.price}>'

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_books = db.Column(db.Integer, default = 0)
    processed_books = db.Column(db.Integer, default = 0)
    cancelled = db.Column(db.Boolean, default = False)

    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #user = db.relationship('User', backref='progress') 