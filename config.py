"""
Settings for the flask app is set here.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base class for all the configs
    """
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_ADMIN = os.environ.get('FLASK_ADMIN') 
    FLASKY_ADMIN_PWD = os.environ.get('ADMIN_PASSWORD')
    FLASKY_MAIL_SENDER = 'Flasky Admin <admin@tactification.com'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    UPLOADED_PHOTOS_DEST = os.getcwd() + '/profile_picture'
    UPLOADED_GIFS_DEST = os.getcwd() + '/gifs'
    FLASKY_POSTS_PER_PAGE = 9
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_FOLLOWERS_PER_PAGE = 10
    OAUTH_CREDENTIALS = {'facebook': {'id': os.environ.get('FB_ID'),
                                      'secret': os.environ.get('FB_SECRET')},
                         'twitter': {'id': os.environ.get('TW_ID'),
	                                    'secret': os.environ.get('TW_SECRET')}
                        }

    @staticmethod
    def init_app(app):
        pass

    def __init__(self):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
                                                                                                'data-dev.sqlite')
    UPLOADED_PHOTOS_DEST = os.getcwd() + '/profile_picture'
    UPLOADED_GIFS_DEST = os.getcwd() + '/gifs'
    FLASKY_POSTS_PER_PAGE = 9
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_FOLLOWERS_PER_PAGE = 10
    FLASKY_MAIL_SUBJECT_PREFIX = '[Tactification]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <tactifiation@gmail.com'
    OAUTH_CREDENTIALS = {'facebook': {'id': os.environ.get('FB_ID'),
                                      'secret': os.environ.get('FB_SECRET')},
                         'twitter': {'id': os.environ.get('TW_ID'),
                                     'secret': os.environ.get('TW_SECRET')}
                         }
    def __init__(self):
        pass

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
                                                                                                 'data-test.sqlite')
    def __init__(self):
        pass

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    def __init__(self):
        pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
