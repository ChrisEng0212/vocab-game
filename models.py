from datetime import datetime, timedelta
from app import app, db, login
from flask_login import UserMixin, current_user # this imports current user, authentication, get id (all the login attributes)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os

try:
    from config import BaseConfig
    DEBUG = BaseConfig.DEBUG    
except:
    DEBUG = os.environ['DEBUG']    

#login manager
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    studentID = db.Column(db.String())
    test = db.Column(db.String())
    
class GamesICC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    players = db.Column(db.String())
    records = db.Column(db.String())
    results = db.Column(db.String())
    winner = db.Column(db.String())
    gameSet = db.Column(db.Integer())

class GamesFRD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    players = db.Column(db.String())
    records = db.Column(db.String())
    results = db.Column(db.String())
    winner = db.Column(db.String())
    gameSet = db.Column(db.Integer())

class GamesWPE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    players = db.Column(db.String())
    records = db.Column(db.String())
    results = db.Column(db.String())
    winner = db.Column(db.String())
    gameSet = db.Column(db.Integer())

class MyModelView(ModelView):
    def is_accessible(self):
        if DEBUG == True:
            return True 
        elif current_user.is_authenticated and current_user.studentID == '100000000':
            return True

admin = Admin(app)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(GamesFRD, db.session))
admin.add_view(MyModelView(GamesICC, db.session))
admin.add_view(MyModelView(GamesWPE, db.session))

