from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from config_glb_vars import photos
 
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
photos = UploadSet('photos', IMAGES)
gifs = UploadSet('gifs', IMAGES)
pagedown = PageDown()
print 'Reaching'

def create_app(config_name):
    print 'create_app:', config_name

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    configure_uploads(app, photos)
    configure_uploads(app, gifs)
    patch_request_class(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .oauth import oauth_rt as oauth_blueprint
    app.register_blueprint(oauth_blueprint, url_prefix='/oauth_rt')
    
    from .api_1_0 import api_rt as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api_rt/v1.0")

    return app
