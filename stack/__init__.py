from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_images import Images
from flask_migrate import Migrate
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '400e932b3856f3c381ae992822469155'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

migrate = Migrate(app, db)
images = Images(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from stack import routes, models
