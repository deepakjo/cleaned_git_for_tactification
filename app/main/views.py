import os
from datetime import datetime, timedelta
from flask import render_template, session, redirect, \
                  url_for, current_app, request, flash, abort, jsonify
from flask_login import login_required, current_user
from decorators import admin_required, permission_required
from forms import BlogCreateForm, BlogFileUploadForm
from werkzeug.utils import secure_filename
from . import main
from .utils import get_pages, get_random_posts
from ..models import User, Post, Comment, Permission
from .. import db, gifs
from ..utils import get_post, get_comment_fields_in_json,  add_comment_to_db


@main.route('/', methods=['GET', 'POST'])
def index():
    post_list = []

    posts = Post.query.order_by(Post.timestamp.desc()).filter_by(is_blog=None).all()
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

    posts = posts[1:]
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
        by_anonymous=True
    except KeyError:
        name = current_user.username
        by_anonymous=False

    try:
        comment = comment_entry['comment']
    except KeyError:
        return jsonify(status_code=400)    

    try:
        post_id = comment_entry['post_id']        
    except KeyError:
        return jsonify(status_code=400)

    comment_in_json = get_comment_fields_in_json(body=comment, author_name=name,by_anonymous=by_anonymous)
    if (comment_in_json.get('result') == 'fail'):
        return jsonify({'result' : 'Fail'})

    post = get_post(comment_entry['post_id'])    
    post_entry = dict()
    post_entry['post'] = post
    comment_in_json.update(post_entry)
    comment_obj = add_comment_to_db(comment_in_json)
    return jsonify(comment_obj.to_json())

@main.route('/play_video', methods = ['POST', 'PUT'])
def play_video():
    post = request.get_json()

    try:
        post_id = post['post_id']
    except KeyError:
        return jsonify({'display' : 0})

    post = get_post(post_id)

    current_time = datetime.utcnow()
    post_time = post.timestamp
    if (current_time > post_time + timedelta(days=7)):
        return jsonify({'result':'pass', 'display': True,
                        'video_id':post.ytVideoId, 'is_embedded': post.get_embedded()})  
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
    post = get_post(id)
    

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
        current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate( \
                page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                error_out=False)
    comments = pagination.items

    #rand_posts = get_random_posts(id)
    return render_template('post.html', post=post, 
                           comments = comments, pagination=pagination,
                           no_of_comments=post.comments.count())

@main.route('/blog_index', methods=['GET', 'POST'])
def blog_index():
    post_list = []

    posts = Post.query.order_by(Post.timestamp.desc()).filter_by(is_blog=True).all()
    page = request.args.get('page', 1, type=int)
    if len(posts) == 0:
        pagination = get_pages(page=page, blog=True)
        return render_template('blog_index.html', posts=post_list, pagination=pagination)
      
    pagination = get_pages(page=page, blog=True)
    posts = pagination.items

    return render_template('blog_index.html', posts=posts, pagination=pagination)

"""
    This function is to display posts and comments.
    Right now adding comments are also in this function. 
    But has to be moved into an async api
    """
@main.route('/blogpost/<id>/<header>', methods = ['GET', 'POST'])
def blogpost(id, header):
    post = get_post(id)
    

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
        current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate( \
                page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                error_out=False)
    comments = pagination.items

    return render_template('blog_post.html', post=post, 
                           comments = comments, pagination=pagination,
                           no_of_comments=post.comments.count())
 
@main.route('/writeBlog', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def writeBlog():
    form = BlogCreateForm()
    if form.validate_on_submit():
        header = form.header.data
        body = form.body.data
        description = form.desc.data
        twTag = form.twTag.data
        tags = form.tags.data
        f = form.photo.data
        filename = secure_filename(f.filename)
        tactic_pic = gifs.save(f, name=filename)
        tactic_url = gifs.url(gifs.get_basename(f.filename))
        try:
            post = Post(body=body, header=header, description=description, twTag=twTag, tags=tags, \
                        tactic_pic=tactic_pic, tactic_url=tactic_url, is_blog=True)
        except:
            return render_template('error.html', msg="Blog post creation failed")

        db.session.add(post)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('main.blog_index'))

    return render_template('write_blog_post.html', form=form)

@main.route('/uploadFile', methods=['GET', 'POST'])
@login_required
@permission_required(permission=Permission.WRITE_ARTICLES)
def uploadFile():

    form = BlogFileUploadForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        tactic_pic = gifs.save(f, name=filename)
        tactic_url = gifs.url(gifs.get_basename(f.filename))
        return redirect(request.args.get('next') or url_for('main.blog_index'))

    return render_template('write_blog_post.html', form=form)

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
