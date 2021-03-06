from flask_wtf import FlaskForm
# what kind of files are allowed to be uploaded
from flask_wtf.file import FileField, FileAllowed, FileRequired
# now we can use this for the account update
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField, validators, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from models import *  


class LoginForm(FlaskForm):
    username = StringField('Player Name', validators=[DataRequired()])
    studentID = StringField('Student ID', validators=[DataRequired()])    
    vocab = RadioField('Vocab', choices = [('FRD_2_2', 'Reading-II-(Units 5-8)'), ('WPE_2_2', 'Workplace-II-(Units 5-8)')], validators=[DataRequired() ])

    submit = SubmitField('Login')

    def validate_username(self, username):  # the field is username
        user = User.query.filter_by(username=username.data).first()  #User was imported at the top # first means just find first instance?
        if user:  # meaning if True
            raise ValidationError('That name has already been used')
