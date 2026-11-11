from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('../config.py')

from app import views
from app.users.views import users_bp
from app.products.views import products_bp
from app.products import storage

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(products_bp)

with app.app_context():
    storage.init_storage()