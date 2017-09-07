from datetime import datetime
from flask import render_template, session, redirect, \
                  url_for, current_app, request, flash, abort, jsonify
from flask_login import login_required, current_user
from decorators import admin_required, permission_required
from . import main
from .forms import PostForm, CommentForm, AnonymousCommentForm
from .utils import get_pages, get_random_posts
from ..models import User, Post, Comment
from ..email import send_email
from ..models import Permission
from .. import db, gifs
from ..utils import get_post, get_comment_fields_in_json,  add_comment_to_db


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    post_list = []

    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
    
        if 'tactical_gif' in request.files:
            filename = gifs.save(form.tactical_gif.data)
            file_url = gifs.url(filename)
        else:
            file_url = None
            
        post = Post(body=form.body.data, header=form.header.data, author=current_user._get_current_object(),
                    tactic_url=file_url, tactic_pic=filename)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    print 'POSTS', posts
    page = request.args.get('page', 1, type=int)
    if posts.__len__() == 0:
        pagination = get_pages(page=page)
        return render_template('index.html', form=form, posts=post_list, pagination=pagination)

    if isinstance(posts[0].author, User):
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
    return render_template('index.html', form=form, posts=posts, pagination=pagination, now_running=now_running)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author or \
        current_user.can(Permission.ADMINISTER):
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        flash('Post has updated')
        return redirect(url_for('.index'))

    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user():
    name = None
    form = NameForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            flash('User is not present')
        else:
            db.session.delete(user)
            db.session.commit()
            flash('User %s is deleted from db' % form.name.data)

            session['name'] = form.name.data
        return redirect(url_for('.index'))

    return render_template('delete_user.html', form=form, name=session.get('name'),
                            current_time=datetime.utcnow())

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.route('/delete_comment/<int:id>/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id, post_id):
    print 'Entering function'
    post=Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(id)
    print current_user.can
    if current_user != comment.author and \
        current_user.can(Permission.ADMINISTER) == False:
        abort(403)

    db.session.delete(comment)
    return redirect(url_for('.post', id=post_id))

@main.route('/ajax_comment', methods = ['POST', 'PUT'])
def ajax_comment():
    entry = request.get_json(force=True)
    print 'comment:', entry

    post = get_post(entry['post_id'])
    comment = entry['comment']
    if (current_user.is_authenticated == False):
        author_name = entry['name']
    else:
        author_name = None

    comment_in_json = get_comment_fields_in_json(body = comment, author_name = author_name)
    if (comment_in_json.get('result') == 'fail'):
        return jsonify({'result' : 'Fail'})

    post_entry = dict()
    post_entry['post'] = post
    comment_in_json.update(post_entry)
    print 'comment_in_json', comment_in_json
    comment_obj = add_comment_to_db(comment_in_json)
    print 'comment_obj', comment_obj.to_json()
    return jsonify(comment_obj.to_json())

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

"""
    This function is to display posts and comments.
    Right now adding comments are also in this function. 
    But has to be moved into an async api
    """
@main.route('/post/<int:id>', methods = ['GET', 'POST'])
def post(id):
    post_entry = {}
    
    post = get_post(id)
    
    if current_user.is_authenticated:
        form = CommentForm()
    else:
        form = AnonymousCommentForm()
        
    if form.validate_on_submit():
        comment_value = form.comment.data
        
        if (current_user.is_authenticated == False):
            author_name = form.name.data
        else:
            author_name = None
            
        comment_in_json = get_comment_fields_in_json(body = comment_value,  author_name = author_name)
        if (comment_in_json.get('result') == 'fail'):
            flash('Your comment failed to publish')
            return redirect(url_for('.post',  id=post.id,  page=-1))
            
        post_entry['post'] = post
        comment_in_json.update(post_entry)
        comment_obj = add_comment_to_db(comment_in_json)
        flash('Your comment has been published')
        return redirect(url_for('.post', id=post.id, page=-1))

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
        current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate( \
                page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                error_out=False)
    comments = pagination.items

    rand_posts = get_random_posts(id)
    return render_template('post.html', post=post, form=form,
                           comments = comments, pagination=pagination,
                           rand_posts = rand_posts, no_of_comments=post.comments.count())

@main.route('/delete_post/<int:id>')
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('.index'))

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))

    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    if current_user.is_followdwed_by(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))

    current_user.unfollow(user)
    flash('You have unfollowed %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                    error_out=False)
    follows = [{'user': item.follower, 'timestamp':item.timestamp}
                                        for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of',
                            endpoint='.followers', pagination=pagination,
                            follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                    error_out=False)
    follows = [{'user': item.followed, 'timestamp':item.timestamp}
                                        for item in pagination.items]
    return render_template('followers.html', user=user, title='Followed by',
                            endpoint='.followed_by', pagination=pagination,
                            follows=follows)

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
