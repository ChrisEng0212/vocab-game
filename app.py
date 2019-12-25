from flask import Flask, render_template   #app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy  #needed for app initialization (see below - db)
from flask_bcrypt import Bcrypt  #needed for password storage
from flask_login import LoginManager, current_user #needed for login
import os



app = Flask(__name__)
app.config.from_object('config.BaseConfig')
db = SQLAlchemy(app)
bcrypt = Bcrypt()
login = LoginManager(app)
login.login_view = 'login' # if user isn't logged in it will redirect to login page
login.login_message_category = 'info'


from routes import *


if __name__ == '__main__': 
    socketio.run(app)
    
    