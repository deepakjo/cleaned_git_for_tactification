from flask import Blueprint

oauth_rt = Blueprint('oauth_rt', __name__)

from . import views 
