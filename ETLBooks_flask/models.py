from datetime import datetime
from flask_tutorial import db, login_manager
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
    posts = db.relationship("Post", backref="author", lazy=True) 

    def __repr__(self):
        return f"User:'{self.username}','{self.email}''{self.image}'"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)   
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    id_User = db.Column(db.Integer,db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"User:'{self.title}','{self.date_posted}''{self.image}'"