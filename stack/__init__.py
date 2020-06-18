from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '772ddfe869f20a33edb4a662e3cbcc41'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/cedric/Desktop/Flaskapp/site.db'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from stack import routes, models
