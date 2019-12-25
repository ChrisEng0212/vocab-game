from datetime import datetime, timedelta
from app import app, db, login
from flask_login import UserMixin, current_user # this imports current user, authentication, get id (all the login attributes)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

#login manager
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    studentID = db.Column(db.String(), nullable=False)
    test = db.Column(db.String())
    #studentID = db.Column(db.String())    

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    players = db.Column(db.String())
    records = db.Column(db.String())
    results = db.Column(db.String())
    winner = db.Column(db.String())
    gameSet = db.Column(db.Integer())

class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.id == 1:
                return True
            else:
                return False
        else:
            # need to change back to false in production mode
            return True

    #https://danidee10.github.io/2016/11/14/flask-by-example-7.html

    
#$2b$12$79FM1YLMP/rLWfznq2iHFelcQ9I6svAZtLFN9.2i1RDQXxq1oPvUS


admin = Admin(app)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Games, db.session))

