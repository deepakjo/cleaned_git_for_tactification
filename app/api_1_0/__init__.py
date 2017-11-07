from flask import Blueprint

api_rt = Blueprint('api', __name__)

from . import authentication, users, posts, errors
