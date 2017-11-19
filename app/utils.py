"""
apps utilities function has to be added in this file
"""
from flask_login import current_user
from app import db
from .models import Comment, Post

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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
    comment = auth_details = anonymous_user = {}
    if body is None:
        return ({'result':'fail', 'error':'comment not provided'})

    comment['body'] = body
    if current_user.is_authenticated:
        auth_details['author_obj'] = current_user._get_current_object()
        
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

    print 'comment_in_json', comment_in_json
    try:
        comment_obj = Comment(body=comment_in_json['body'], post=comment_in_json['post'],
                              author=current_user._get_current_object(), 
                              by_anonymous=comment_in_json['by_anonymous'])
    except KeyError:
        author_name = comment_in_json['author_name']
        comment_obj = Comment(body=comment_in_json['body'], post=comment_in_json['post'],
                              anonymous_user_name=author_name, by_anonymous=comment_in_json['by_anonymous'])

    db.session.add(comment_obj)
    db.session.commit()
    return comment_obj
