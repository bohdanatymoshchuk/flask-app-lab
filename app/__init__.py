from flask import Flask

app = Flask(__name__)

from .users import views
from .users.views import users_bp

app.register_blueprint(users_bp)