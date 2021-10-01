import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect

app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('SERVER_EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('SERVER_EMAIL_PASSWORD')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY')

access_code = ['0910327782404461760d55db4f8d03f5943681aa', '7c31e9858984c27a8ef5ab6761e2052b0c4d4034']

db = SQLAlchemy(app)
# db.create_all()  # Create new database. This code is used when database needs to be reset

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Login Required'

mail = Mail(app)

num_power = 3  # 1 for 1 kB, 2 for 1 MB, 3 for 1 GB, 4 for 1 TB
num_unit = 10  # Number of times per unit
max_size = (1024**num_power) * num_unit  # 10GB.

CSRFProtect(app)

from NAS_Family import Route
