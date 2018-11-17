from flask import jsonify, request, g, url_for, current_app
from flask_login import current_user
from . import api_rt
from errors import forbidden
from ..models import Post, Permission, User, Comment
from decorators import permission_required
from .. import db,  gifs
from ..utils import get_post, get_comment_fields_in_json,  add_comment_to_db
    
@api_rt.route('/new_post', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
 
    file_tuples = []

    if 'tactical_gif' in request.files:
        print request.files['tactical_gif']
        filename = gifs.save(request.files['tactical_gif'])
        file_url = gifs.url(filename)
        file_details = (filename,  file_url)
        file_tuples.append(file_details)
        print "file_url=%s file_details=%s" %(file_url,  file_details)
    else:
        print 'Else'
        raise ValidationError('File is a must for POST')
        return jsonify('Error')

    if 'tactical_pic_1750' in request.files:
        print request.files['tactical_pic_1750']
        filename = gifs.save(request.files['tactical_pic_1750'])
        file_url = gifs.url(filename)
        file_details = (filename,  file_url)
        file_tuples.append(file_details)
        print "file_url=%s file_details=%s" %(file_url,  file_details)
    else:
        print 'Else'
        raise ValidationError('File is a must for POST')
        return jsonify('Error')

    if 'tactical_pic_1575' in request.files:
        print request.files['tactical_pic_1575']
        filename = gifs.save(request.files['tactical_pic_1575'])
        file_url = gifs.url(filename)
        file_details = (filename,  file_url)
        file_tuples.append(file_details)
        print "file_url=%s file_details=%s" %(file_url,  file_details)
    else:
        print 'Else'
        raise ValidationError('File is a must for POST')
        return jsonify('Error')

    if 'tactical_pic_875' in request.files:
        print request.files['tactical_pic_875']
        filename = gifs.save(request.files['tactical_pic_875'])
        file_url = gifs.url(filename)
        file_details = (filename,  file_url)
        file_tuples.append(file_details)
        print "file_url=%s file_details=%s" %(file_url,  file_details)
    else:
        print 'Else'
        raise ValidationError('File is a must for POST')
        return jsonify('Error')

    print 'type of file_tuples:', type(file_tuples)
    post = Post.from_json(request.form,  file_tuples)
    post.author = g.current_user
    post.author_id = g.current_user.id
    print 'author.id', g.current_user.id
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
	       {'Location': url_for('api.api_rt_get_post', id=post.id, _external=True)}


@api_rt.route('/edit_post/<int:id>', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    """
    :type id: int
    """
    post = Post.query.get_or_404(id)
    print 'edit_post', id
    try: 
        body = request.form['body']       
    except KeyError:
        raise KeyError
        
    try:
        header = request.form['header']
    except KeyError:
        raise KeyError

    try:
        hashTag = request.form['twTag']    
    except KeyError:
        raise KeyError

    if 'tactical_gif' in request.files:
        print request.files['tactical_gif']
        filename = gifs.save(request.files['tactical_gif'])
        file_url = gifs.url(filename)
        file_details = (filename,  file_url)
        print "file_url=%s file_details=%s" %(file_url,  file_details)

    post.body = body
    post.header = header
    post.twTag = hashTag
    post.author = g.current_user
    post.tactic_pic = file_details[0]
    post.tactic_url = file_details[1]
    post.author_id = g.current_user.id
    print 'author.id', g.current_user.id    
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
	       {'Location': url_for('api.api_rt_get_post', id=post.id, _external=True)}

@api_rt.route('/delete_post/<int:id>', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def delete_post(id):
    """
    :type id: int
    """
    print 'postid:', id
    post = get_post(id)

    if post is None:
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return jsonify({'result': 'fail', "count": len(posts)}) 

    print 'post', post             
    db.session.delete(post)
    db.session.commit()
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify({'result': 'pass', "count": len(posts)})

@api_rt.route('/number_of_posts', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def number_of_posts():
    """ API to add comment through RESTful Calls 
     inputs: post id
     """
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify({"count": len(posts)})

@api_rt.route('/post_comment/<int:id>', methods=['PUT'])
@permission_required(Permission.COMMENT)
def api_rt_post_comment(id):
    post_entry = {}
    print 'id',  id

    post = get_post(id)
        
    comment_args = request.get_json(force=True)   
    try: 
        comment_value = comment_args['comment']      
    except KeyError:
        comment_value = None
        
    try:
        author_name =  comment_args['name']  
    except KeyError:
        author_name = None
        
    comment_in_json = get_comment_fields_in_json(body = comment_value,  author_name = author_name)
    if (comment_in_json.get('result') == 'fail'):
        return jsonify(comment_in_json)
        
    post_entry['post'] = post
    comment_in_json.update(post_entry)
    comment_obj = add_comment_to_db(comment_in_json)
    return  jsonify(comment_obj.to_json(),  {'Location': url_for('api.api_rt_get_post', id=comment_obj.post_id, _external=True)})
    
@api_rt.route('/add_video/<int:id>', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)    
def api_rt_update_yt_Video(id):
    post = get_post(id)

    try:
        videoId = request.form['videoId']
    except KeyError:
        raise KeyError

    try:
        isEmbedded = request.form['isEmbedded']
    except KeyError:
        raise KeyError

    post.ytVideoId = videoId
    post.set_embedded(isEmbedded)

    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
	       {'Location': url_for('api.api_rt_get_post', id=post.id, _external=True)}      

@api_rt.route('/posts_view')
def get_posts():
	print 'post', g.current_user
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
	                                 error_out=False)
	posts = pagination.items
	print 'page', pagination.__dict__
	print 'post', posts
	print 'prev', pagination.has_prev
	print 'next', pagination.has_next
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_posts', page=page - 1, _external=True)
		
	next = None
	if pagination.has_next:
		next = url_for('api.get_posts', page=page + 1, _external=True)
		
	return jsonify({'posts': [post.to_json() for post in posts],
	                'prev': prev,
	                'next': next,
	                'count': pagination.total})


@api_rt.route('/posts/<int:id>')
def api_rt_get_post(id):
	print 'get_post'
	post = Post.query.get_or_404(id)
	return jsonify(post.to_json())

@api_rt.route('/user/<int:id>')
def get_user_info(id):
	print 'get_user'
	user = User.query.get_or_404(id)
	return jsonify(user.to_json())

@api_rt.route('/comments/<int:id>')
def get_post_comments(id):
	print 'get_post_comments'
	comment = Comment.query.get_or_404(id)
	return jsonify(comment.to_json())
