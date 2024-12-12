from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField,SelectField,IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ETLBooks_flask.models import User

class RegistrationForm(FlaskForm):
    username = StringField("Username",
                            validators = [DataRequired(),Length(min= 2, max= 20)])
    email = StringField("Email",
                            validators = [DataRequired(),Email()])
    password = PasswordField("Password", 
                             validators=[DataRequired()])
    confirm_password = PasswordField("Confrim Password", 
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign up")

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("That username is taken! Please choose another one")
        
    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("That email is taken! Please choose another one")
        
            

class LoginForm(FlaskForm):
    email = StringField("Email",
                            validators = [DataRequired(),Email()])
    password = PasswordField("Password", 
                             validators=[DataRequired()])
    remember = BooleanField("Remember me")

    submit = SubmitField("Login in")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username",
                            validators = [DataRequired(),Length(min= 2, max= 20)])
    email = StringField("Email",
                            validators = [DataRequired(),Email()])
    picture = FileField("Update Profile Picture",
                         validators=[FileAllowed(["jpg","png"])])
    submit = SubmitField("Update")

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("That username is taken! Please choose another one")
        
    def validate_email(self,email):
        if email.data != current_user.email:
            email = User.query.filter_by(email = email.data).first()
            if email:
                raise ValidationError("That username is taken! Please choose another one")
            
class BookForm(FlaskForm):
    title = StringField("Title",
                        validators=[DataRequired(),Length(min=1, max=255)])
    price = DecimalField("Price",
                         validators=[DataRequired()])
    review = SelectField(choices=[('One', 'One'), ('Two', 'Two'), ('Three', 'Three'), ('Four', 'Four'), ('Five', 'Five')])
    category = StringField("Category",
                            validators=[DataRequired(),Length(min=1,max=255)])
    availability = BooleanField("Available?",
                                 validators=[DataRequired()])
    stock = IntegerField("Stock", 
                         validators=[DataRequired()])
    image = FileField("Book cover", validators=[FileAllowed(["jpg","png"])])       