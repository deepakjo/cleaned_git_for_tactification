from flask_login import current_user
from models import Comment,  Post
from app import db

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
def get_post(id):           
    post = Post.query.get_or_404(id)
    print 'post',  post
    if post is None:
        return None
        
    return post

def get_comment_fields_in_json(body,  author_name=None):
    comment = auth_details = anonymous_user = {}
    
    if body is None:
        return ({'result' : 'fail',  'error' : 'comment not provided'})
        
    comment['body'] = body
    if (current_user.is_authenticated):
        auth_details['author_obj'] = current_user._get_current_object()
    else:
        if (author_name == None):
             return ({'result' : 'fail',  'error' : 'name not provided'})
             
        anonymous_user['author_name'] = author_name
    
    comment_in_json = dict()
    comment_in_json['result'] = 'pass'
    comment_in_json.update(comment)
    comment_in_json.update(auth_details)
    comment_in_json.update(anonymous_user)
    return (comment_in_json)
  
def add_comment_to_db(comment_in_json):  

    try:
        author = comment_in_json['author_obj']
        comment_obj = Comment(body = comment_in_json['body'],  post = comment_in_json['post'],
                                                   author = current_user._get_current_object())
    except KeyError:
        author_name = comment_in_json['author_name']
        comment_obj = Comment(body = comment_in_json['body'],  post = comment_in_json['post'],
                                                   anonymous_user_name = author_name,  by_anonymous = True)        
        
    db.session.add(comment_obj)
    db.session.commit()
    return comment_obj
    
    
