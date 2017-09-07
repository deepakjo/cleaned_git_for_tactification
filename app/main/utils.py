import random
"""current_app is to get the config params"""
from flask import current_app
from ..models import Post

def get_pages(page=1):
    """ util API to get the entries in page """

    if (page == 1):
        per_page = current_app.config['FLASKY_POSTS_PER_PAGE'] + 1
        print 'if per_page', per_page
    else:
        per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
        print 'else per_page', per_page


    pages = Post.query.order_by(Post.timestamp.desc()).paginate(page, \
                                per_page=per_page, \
                                error_out=False)

    return pages

"""
    This functions is to get 4 random posts to be 
    displayed under a post.
"""
def get_random_posts(id):
    rand_posts = []
    rand_numbers = []

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    if (posts is None):
        return None

    rand_numbers = random.sample(range(1, len(posts)), 5)

    print 'list of rand_numbers', rand_numbers

    try: 
        rand_numbers.remove(id)
    except ValueError:
        rand_numbers.pop(4)

    for id in range(4):
        idx = rand_numbers[id]
        rand_posts.append(posts[idx])

    return rand_posts        