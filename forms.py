from flask_wtf import FlaskForm
# what kind of files are allowed to be uploaded
from flask_wtf.file import FileField, FileAllowed, FileRequired
# now we can use this for the account update
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField, validators, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from models import *  # you forgot this and it took forever to notice the mistake!!!


class LoginForm(FlaskForm):
    username = StringField('Player Name', validators=[
                            DataRequired()])
    studentID = StringField('Student ID', validators=[
                            DataRequired()])
    #password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
