from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, url_for,  g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
#for pictures and gifs
from . import photos, gifs
from markdown import markdown
import bleach
from exceptions import ValidationError

#pg112
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x2
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x8
    ADMINISTER = 0x80

#pg 54: Model definition. Tables are represented as models thru class.
class Role(db.Model):
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
        roles = {'User' : (Permission.FOLLOW | Permission.COMMENT | \
                            Permission.WRITE_ARTICLES, True), \
                'Moderator' : (Permission.FOLLOW | Permission.COMMENT | \
                            Permission.WRITE_ARTICLES | \
                            Permission.MODERATE_COMMENTS, False), \
                'Administrator' : (Permission.FOLLOW | Permission.COMMENT | \
                            Permission.WRITE_ARTICLES | \
                            Permission.MODERATE_COMMENTS |
                            Permission.ADMINISTER, False)}
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)

            role.permissions = roles[r][0]    
            role.default = roles[r][1]    
            db.session.add(role)

        db.session.commit()

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #pg 95
    #pg 66. When add new fields, upgrade the db.
    email = db.Column(db.String(64), unique=True, index=True)
    #TODO: username not a must to be unique.
    username = db.Column(db.String(32), unique=True, index=True)
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

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        print password
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def member_since_join(self):
        member_since = datetime.utcnow()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            print 'email', self.email
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role(permissions=0xff)

            if self.role is None:
                self.role = Role(permissions=(Permission.FOLLOW | Permission.COMMENT))

        self.member_since_join()

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self, permissions):
        return (self is not None and (self.role.permissions & permissions == permissions))

    def is_administrator(self):
        return (self.can(Permission.ADMINISTER))

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
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
        return photos.url(self.profile_pic)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            filename = 'anonymous.jpeg'
            file_url = photos.url(filename)
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True),
                     profile_pic = filename, profile_url = file_url)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            return True
        else:
            return False

    def is_followed_by(self, user):
        f = self.followers.filter_by(follower_id=user.id).first()
        if f:
            return True
        else:
            return False

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'id' : self.email})
	
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
            
        return data['id']
    
    def to_json(self):
        json_post = {'url': url_for('api.get_user', id=self.id, _external=True),
                     'username': self.username,
                     'member_since': self.member_since,
                     'last_seen': self.last_seen,
                     'followed_posts': url_for('api.get_post_comments', id=self.id, _external=True),
                     'post_count': self.posts.count()
                     }
        
        return json_post
    
class AnonymousUser(AnonymousUserMixin):
    
    def can(self, permissions):
        if permissions == Permission.COMMENT:
            return (True)
        
        return (False)

    def is_administrator(self):
        return (False)

login_manager.anonymous_user = AnonymousUser

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    header = db.Column(db.String(32))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # using flask-uploads
    tactic_pic = db.Column(db.String(64))
    tactic_url = db.Column(db.String(64))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockqoute', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,
                                                                output_format='html'),
                                                        tags=allowed_tags, strip=True))
    
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
    
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True), author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def add_gifs_for_all_posts(gif, header):
        for post in Post.query.all():
            post.tactic_pic = gif
            post.tactic_url = gifs.url(post.tactic_pic)
            post.header = header
            db.session.add(post)
            db.session.commit()
    
    def render_tactics_pic(self):
        return self.tactic_url
    
    def render_post(self):
        tweet = self.header
        tweet.replace(' ', '%20')
        print 'HEADER', tweet
        return tweet
    
    def render_url(self):
        url = url_for('main.post', id=self.id, _external=True)
        url.replace(':', '%3A')
        url.replace('/', '%2F')
        print 'URL', url
        return url

    def to_json(self):
        json_post = {
            'url' : url_for('api.api_rt_get_post', id=self.id, _external=True),
            'header' : self.header,
            'body' : self.body,
            'timestamp' : self.timestamp,
            'author' : url_for('api.get_user', id=self.author_id, _external=True),
            'comments' : url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count()
        }
        
        return json_post
    
    @staticmethod
    def from_json(json_post,  file_details):
        try: 
            body = json_post.get('body')       
        except KeyError:
            raise KeyError
        try:
            header = json_post.get('header')
        except KeyError:
            raise KeyError
            
        return Post(body=body,  header=header, 
                            tactic_pic=file_details[0],  tactic_url=file_details[1])
    
db.event.listen(Post.body, 'set', Post.on_changed_body)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    by_anonymous = db.Column(db.Boolean)
    anonymous_user_name = db.Column(db.String(32))
 
    def __init__(self,  body, post = None,  author = None, 
                        anonymous_user_name=None, 
                        by_anonymous = False):
        self.body = body
        self.post = post
        self.author = author
        self.anonymous_user_name = anonymous_user_name
        self.by_anonymous = by_anonymous

    def to_json(self):
        print 'reached to_json'
        user_url = None

        if (self.by_anonymous == True):
            profile_pic_url = url_for('static', filename = 'anonymous.jpg', _external=True)
            uname = self.anonymous_user_name
        else:
            profile_pic_url = self.author.profile_pic_url()
            user_url = url_for('.user', username=self.author.username)
            uname = self.author.username

        json_post = {
            'url' : url_for('api.api_rt_get_post', id=self.post_id, _external=True),
            'id': self.id,
            'comment' : self.body,
            'ts' : self.timestamp,
            'is_anon' : self.by_anonymous,
            'pfl_pic' : profile_pic_url,
            'url_for_u' : user_url,
            'uname' : uname, 
            'ts' : self.timestamp.utcnow()
        }

        print 'JSON_POST', json_post        
        return json_post
