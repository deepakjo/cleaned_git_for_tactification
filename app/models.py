"""
all db classes and attributes are defined in this function
"""
from datetime import datetime
from random import sample
from HTMLParser import HTMLParser
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for, Markup
from flask_login import UserMixin, AnonymousUserMixin
from avinit import get_avatar_data_url
from bleach import clean
from app import db
from . import login_manager
#for pictures and gifs
from . import photos

DEFAULT_COLORS = [
    "#1abc9c", "#16a085", "#f1c40f", "#f39c12", "#2ecc71", "#27ae60",
    "#e67e22", "#d35400", "#3498db", "#2980b9", "#e74c3c", "#c0392b",
    "#9b59b6", "#8e44ad", "#bdc3c7", "#34495e", "#2c3e50", "#95a5a6",
    "#7f8c8d", "#ec87bf", "#d870ad", "#f69785", "#9ba37e", "#b49255",
    "#b49255", "#a94136",
]

#pg112
class Permission:
    """
    user permissions are defined here
    """
    COMMENT = 0x1
    WRITE_ARTICLES = 0x02
    MODERATE_COMMENTS = 0x4
    ADMINISTER = 0x8

#pg 54: Model definition. Tables are represented as models thru class.
class Role(db.Model):
    """
    roles of users are defined in this class
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    #pg 112
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    #pg 56. backref will create an attribute named 'role' to User.
    #it can be used to access 'Role' from 'User' instead of 'role_id' in user.
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        """
        inserting roles
        """
        roles = {'User' : (Permission.COMMENT, True),
                'Moderator' : (Permission.COMMENT | \
                            Permission.WRITE_ARTICLES | \
                            Permission.MODERATE_COMMENTS, False), \
                'Administrator' : (Permission.COMMENT | \
                            Permission.WRITE_ARTICLES | \
                            Permission.MODERATE_COMMENTS | \
                            Permission.ADMINISTER, False)}
        for r in roles:
            role = Role(name=r)

            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)

        db.session.commit()

class User(db.Model, UserMixin):
    """
    all user related information is stored here.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #pg 95
    #pg 66. When add new fields, upgrade the db.
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(32))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active = db.Column(db.Boolean)
    name = db.Column(db.String(32))
    country = db.Column(db.String(32))
    location = db.Column(db.String(32))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    via_oauth = db.Column(db.Boolean, default=False)
    # using flask-uploads
    profile_pic = db.Column(db.String(64))
    profile_url = db.Column(db.String(64))
    #pg 91
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        password setter
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        verifying password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        username
        """
        return '<User %r>' % self.username
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def member_since_join(self):
        """
        date of join
        """
        member_since = datetime.utcnow()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.member_since_join()

    def ping(self):
        """
        for experiment
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self, permissions):
        """
        have sufficient permissions
        """
        print('Permissions: {:d} passed permissions: {:d}'.format(self.role.permissions, permissions))
        return self is not None and (self.role.permissions and self.role.permissions & permissions)

    def is_administrator(self):
        """
        is adminstrator
        """
        return self.can(Permission.ADMINISTER)

    def generate_confirmation_token(self, expiration=3600):
        """
        generate the token for user.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        """
        to set confirm. right now, its used anywhere
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        return True

    def profile_pic_url(self, size=10, default='identicon', rating = 'g'):
        """
        To pass users profile picture
        """
        return photos.url(self.profile_pic)

    def generate_auth_token(self, expiration):
        """
        To generate authentication via rest
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id' : self.email})

    @staticmethod
    def verify_auth_token(token):
        """
        for verification of authentication via rest
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None

        return data['id']
 
    def to_json(self):
        json_post = {'url': url_for('api.get_user_info', id=self.id, _external=True),
                     'username': self.username,
                     'member_since': self.member_since,
                     'last_seen': self.last_seen,
                     'followed_posts': url_for('api.get_post_comments', id=self.id, _external=True),
                     'post_count': self.posts.count()
                    }

        return json_post

class AnonymousUser(AnonymousUserMixin):
    """
    class for anonymous users
    """
    def can(self, permissions):
        """
        can user comment or not? 
        """
        if permissions == Permission.COMMENT:
            return True
        return False

    def is_administrator(self):
        """
        return false always under anonymousUser 
        """
        return False

login_manager.anonymous_user = AnonymousUser

class Post(db.Model):
    """
    All post data is stored here.
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    header = db.Column(db.String(32))
    description = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # using flask-uploads
    # This is used for main page
    tactic_pic = db.Column(db.String(64))
    tactic_url = db.Column(db.String(64))

    tactic_pic_1750px = db.Column(db.String(64))
    tactic_url_1750px = db.Column(db.String(64))
    tactic_pic_1575px = db.Column(db.String(64))
    tactic_url_1575px = db.Column(db.String(64))
    tactic_pic_875px = db.Column(db.String(64))
    tactic_url_875px = db.Column(db.String(64))

    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    ytVideoId = db.Column(db.String(32))
    is_embedded = db.Column(db.Boolean)
    twTag = db.Column(db.String(32))
    tags = db.Column(db.String(32))
    is_blog = db.Column(db.Boolean)

    def post_date_in_isoformat(self):
        date_str = self.timestamp.isoformat()[:10]
        date_list = date_str.split('-')[::-1]
        return '{:s}-{:s}-{:s}'.format(date_list[0], date_list[1], date_list[2]) 

    def body_clean(self):
        start_idx=self.body.find('<div style="color:black">') + self.body.find('>') +1
        end_idx=self.body.find('</div>') 
        return (self.body[start_idx:end_idx])
 
    def set_embedded(self, isEmbedded=0):
        if isEmbedded == u'0':
            self.is_embedded = 0
        else:
            self.is_embedded = 1

    def get_embedded(self):
        if (self.is_embedded == False):
            return False
        else:
            return True

    def markup_body(self):
        return Markup(self.body)

    def render_tactics_pic(self):
        """
        for passing the url for image to html files. Have to check if it's
        used anywhere.
        """
        return self.tactic_url
 
    def render_post(self):
        """
        created for passing post for html files. Have to check if 
        it is used anywhere.
        """
        tweet = self.header
        tweet.replace(' ', '%20')
        print 'HEADER', tweet
        return tweet
 
    def render_url(self):
        """
        created for passing url for html files. Have to check if 
        it is used anywhere.
        """
        url = url_for('main.post', id=self.id, _external=True)
        url.replace(':', '%3A')
        url.replace('/', '%2F')
        print 'URL', url
        return url

    def to_json(self):
        """
        To convert post db entry to json info for rest api.
        """
        json_post = {
            'url' : url_for('api.api_rt_get_post', id=self.id, _external=True),
            'header' : self.header,
            'body' : self.body,
            'timestamp' : self.timestamp,
            'author' : url_for('api.get_user_info', id=self.author_id, _external=True),
            'comments' : url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count(),
            'videoId': self.ytVideoId,
            'isEmbedded': self.get_embedded()
        }
        return json_post
 
    @staticmethod
    def from_json(json_post, file_tuples):
        """
        To convert rest api json info to a post.
        """
        try:
            body = json_post.get('body')
        except KeyError:
            raise KeyError
        try:
            header = json_post.get('header')
        except KeyError:
            raise KeyError

        try:
            twTag = json_post.get('twTag')
        except KeyError:
            raise KeyError

        print 'from json:', type(file_tuples)
        tactic_pic_tuple = file_tuples.pop(0)
        tactic_pic=tactic_pic_tuple[0]
        tactic_url=tactic_pic_tuple[1]

        tactic_pic_1750px_tuple=file_tuples.pop(0)
        tactic_pic_1750px = tactic_pic_1750px_tuple[0]
        tactic_url_1750px = tactic_pic_1750px_tuple[1]

        tactic_pic_1575px_tuple=file_tuples.pop(0)
        tactic_pic_1575px = tactic_pic_1575px_tuple[0]
        tactic_url_1575px = tactic_pic_1575px_tuple[1]

        tactic_pic_875px_tuple=file_tuples.pop(0)
        tactic_pic_875px = tactic_pic_875px_tuple[0]
        tactic_url_875px = tactic_pic_875px_tuple[1]

        return Post(body=body, header=header, twTag=twTag, \
                    tactic_pic=tactic_pic, tactic_url=tactic_url, \
                    tactic_pic_1750px=tactic_pic_1750px, tactic_url_1750px=tactic_url_1750px, \
                    tactic_pic_1575px=tactic_pic_1575px, tactic_url_1575px=tactic_url_1575px, \
                    tactic_pic_875px=tactic_pic_875px,tactic_url_875px=tactic_url_875px)
 
@login_manager.user_loader
def load_user(user_id):
    """
    """
    return User.query.get(int(user_id))

class Comment(db.Model):
    """
    comment db stores all the comments in the post.
    post references into this table for each post.
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    by_anonymous = db.Column(db.Boolean)
    anonymous_user_name = db.Column(db.String(32))
 
    def __init__(self, body=None, post=None, author=None,
                 anonymous_user_name=None,
                 by_anonymous=False):
        self.body = body
        self.post = post
        if by_anonymous:
            self.anonymous_user_name = anonymous_user_name
        else:    
            self.author = author
        
        self.by_anonymous = by_anonymous

    def get_anonymous_pic(self, username, anonymous=True):
        if username is None:
            print 'returning'
            return

        colors = list()
        color_list = sample(range(1, len(DEFAULT_COLORS)), 3)
        for color in color_list:
            colors.append(DEFAULT_COLORS[color])

        if anonymous is False:
            user =  User.query.filter_by(id=self.author_id).first()
            if user is None:
                return
            username = user.username
            
        data = get_avatar_data_url(username, colors=colors)
        return data

    def to_json(self):
        """
        api to convert to json for rest apis and ajax calls
        """

        # will add if profile pic is mandatory while registering.
        #else:
        #    profile_pic_url = self.author.profile_pic_url()
        if self.by_anonymous:
            uname = self.anonymous_user_name
        else:
            uname = self.author.username

        profile_pic_url = self.get_anonymous_pic(uname)

        json_post = {
            'url' : url_for('api.api_rt_get_post', id=self.post_id, _external=True),
            'id': self.id,
            'comment' : self.body,
            'ts' : self.timestamp,
            'is_anon' : self.by_anonymous,
            'pfl_pic' : profile_pic_url,
            'uname' : uname
        }

        print 'JSON_POST', json_post
        return json_post
