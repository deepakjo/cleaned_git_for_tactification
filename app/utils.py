"""
apps utilities function has to be added in this file
"""
from random import sample
from flask_login import current_user
from avinit import get_avatar_data_url
from app import db
from .models import Comment, Post
from .main import main

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
DEFAULT_COLORS = [
    "#1abc9c", "#16a085", "#f1c40f", "#f39c12", "#2ecc71", "#27ae60",
    "#e67e22", "#d35400", "#3498db", "#2980b9", "#e74c3c", "#c0392b",
    "#9b59b6", "#8e44ad", "#bdc3c7", "#34495e", "#2c3e50", "#95a5a6",
    "#7f8c8d", "#ec87bf", "#d870ad", "#f69785", "#9ba37e", "#b49255",
    "#b49255", "#a94136",
]

def allowed_file(filename): 
    """
    types of files allowed to store in db.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_post(id):
    """
    finding if the id passed is valid and return the post representing id.
    """
    post = Post.query.get_or_404(id)
    print 'post', post
    if post is None:
        return None
    return post

def get_comment_fields_in_json(body, author_name=None, by_anonymous=False):
    """
    getting comment fields in the form of json.
    """
    print 'to json', body, author_name, by_anonymous
    comment = auth_details = anonymous_user = {}
    if body is None:
        return ({'result':'fail', 'error':'comment not provided'})

    comment['body'] = body
    if current_user.is_authenticated:
        auth_details['author_obj'] = current_user._get_current_object()
        print auth_details['author_obj'].__dict__
        
    else:
        if author_name is None:
            return ({'result' : 'fail', 'error' : 'name not provided'})
        anonymous_user['author_name'] = author_name

    comment_in_json = dict()
    comment_in_json['result'] = 'pass'
    comment_in_json['by_anonymous'] = by_anonymous
    comment_in_json.update(comment)
    comment_in_json.update(auth_details)
    comment_in_json.update(anonymous_user)
    return comment_in_json

def add_comment_to_db(comment_in_json):
    """
    adding comments into the db.
    """

    if comment_in_json['by_anonymous'] is False:
        comment_obj = Comment(body=comment_in_json['body'], post=comment_in_json['post'],
                              author=current_user._get_current_object(), 
                              by_anonymous=comment_in_json['by_anonymous'])
    else:
        author_name = comment_in_json['author_name']
        comment_obj = Comment(body=comment_in_json['body'], post=comment_in_json['post'],
                              anonymous_user_name=author_name, by_anonymous=comment_in_json['by_anonymous'])

    db.session.add(comment_obj)
    db.session.commit()
    return comment_obj

@main.context_processor
def anonymous_utility_processor():
    def get_anonymous_pic(username):
        if username is None:
            print 'returning'
            return

        colors = list()
        color_list = sample(range(1, len(DEFAULT_COLORS)), 3)
        for color in color_list:
            colors.append(DEFAULT_COLORS[color])

        data = get_avatar_data_url(username, colors=colors)
        return data

    return dict(get_anonymous_pic = get_anonymous_pic)
