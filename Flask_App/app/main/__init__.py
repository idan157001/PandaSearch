from flask import Blueprint
main = Blueprint('main', __name__)

from app.main import routes
from .db import FireBase
database = FireBase()