from flask import Flask, render_template   #app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy  #needed for app initialization (see below - db)
from flask_bcrypt import Bcrypt  #needed for password storage
from flask_login import LoginManager, current_user #needed for login
from flask_socketio import SocketIO #https://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent/page/12
import os
try:
    from config import BaseConfig
    DEBUG = BaseConfig.DEBUG
    SECRET_KEY = BaseConfig.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = BaseConfig.SQLALCHEMY_DATABASE_URI     
except:
    DEBUG = os.environ['DEBUG']
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    

app = Flask(__name__)
app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI   
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#socketio = SocketIO(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt()
login = LoginManager(app)
login.login_view = 'login' # if user isn't logged in it will redirect to login page
login.login_message_category = 'info'

socketio = SocketIO(app, manage_session=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


from routes import *


if __name__ == '__main__':
    socketio.run(app)
    
    