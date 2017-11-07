from datetime import datetime, timedelta
from flask import render_template, session, redirect, \
                  url_for, current_app, request, flash, abort, jsonify
from flask_login import login_required, current_user
from decorators import admin_required, permission_required
from . import main
from .utils import get_pages, get_random_posts
from ..models import User, Post, Comment
from ..models import Permission
from .. import db, gifs
from ..utils import get_post, get_comment_fields_in_json,  add_comment_to_db


@main.route('/', methods=['GET', 'POST'])
def index():
    post_list = []

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    print 'POSTS', posts
    page = request.args.get('page', 1, type=int)
    if posts.__len__() == 0:
        pagination = get_pages(page=page)
        return render_template('index.html', posts=post_list, pagination=pagination)

    now_running=posts[0]
        
    pagination = get_pages(page=page)
    posts = pagination.items

    for post in posts:
        if isinstance(post.author, User):
            post_list.append(post)

    if (page == 1):
        posts = posts[1:]
    else:
        posts = posts

    print 'posts', posts
    return render_template('index.html', posts=posts, pagination=pagination, now_running=now_running)

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.route('/submit_comment', methods = ['POST', 'PUT'])
def submit_comment():

    print request.headers
    print request.__dict__
    print request.get_json()

    comment_entry = request.get_json()
    try:
        name = comment_entry['name']
    except KeyError:
        name = current_user.name

    try:
        comment = comment_entry['comment']
    except KeyError:
        return jsonify(status_code=400)    

    try:
        post_id = comment_entry['post_id']        
    except KeyError:
        return jsonify(status_code=400)

    comment_in_json = get_comment_fields_in_json(body = comment, author_name = name)
    if (comment_in_json.get('result') == 'fail'):
        return jsonify({'result' : 'Fail'})

    post = get_post(comment_entry['post_id'])    
    post_entry = dict()
    post_entry['post'] = post
    comment_in_json.update(post_entry)
    print 'comment_in_json', comment_in_json
    comment_obj = add_comment_to_db(comment_in_json)
    print 'comment_obj', comment_obj.to_json()
    return jsonify(comment_obj.to_json())

@main.route('/play_video', methods = ['POST', 'PUT'])
def play_video():
    post = request.get_json()
    try:
        post_id = post['post_id']
    except KeyError:
        return jsonify({'display' : 0})

    post = get_post(post_id)
    print 'post_id', post_id

    print 'timestamp:', post.timestamp
    print 'timedelta:', timedelta(days=7)
    print 'utc:', datetime.utcnow()
    print 'post video', post.ytVideoId
    current_time = datetime.utcnow()
    post_time = post.timestamp
    if (current_time > post_time + timedelta(minutes=5)):
        return jsonify({'result':'pass', 'display': True,
                        'video_id':post.ytVideoId})    
    else:
        date_of_posting = post.timestamp + timedelta(days=7)
        return jsonify({'result':'pass', 'display': False, 'date': date_of_posting.strftime("%m/%d/%Y")})

"""
    This function is to display posts and comments.
    Right now adding comments are also in this function. 
    But has to be moved into an async api
    """
@main.route('/post/<int:id>', methods = ['GET', 'POST'])
def post(id):
    post_entry = {}
    
    post = get_post(id)
    

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
        current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate( \
                page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                error_out=False)
    comments = pagination.items

    rand_posts = get_random_posts(id)
    return render_template('post.html', post=post, 
                           comments = comments, pagination=pagination,
                           rand_posts = rand_posts, no_of_comments=post.comments.count())

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        print '404'
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        print '500'
        abort(500)
    shutdown()
    print 'shutting down'
    return 'Shutting Down'        
