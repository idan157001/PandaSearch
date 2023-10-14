from flask import Flask

from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



app = Flask(__name__,static_folder='static')
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)
app.config.from_object(Config)

from app.main import main as main_blueprint
app.register_blueprint(main_blueprint)