import random
"""current_app is to get the config params"""
from flask import current_app
from ..models import Post

def get_pages(page=1, blog=None):
    """ util API to get the entries in page """

    if (page == 1):
        per_page = current_app.config['FLASKY_POSTS_PER_PAGE'] + 1
        print 'if per_page', per_page
    else:
        per_page = current_app.config['FLASKY_POSTS_PER_PAGE'] + 1
        print 'else per_page', per_page

    pages = Post.query.order_by(Post.timestamp.desc()).filter_by(is_blog=blog).paginate(page,
                                per_page=per_page, \
                                error_out=False)

    posts = Post.query.filter_by(is_blog=blog)
    return pages        


"""
    This functions is to get 4 random posts to be 
    displayed under a post.
"""
def get_random_posts(id, blog=None):
    rand_posts = []
    rand_numbers = []

    posts = Post.query.filter_by(is_blog=blog)
    if posts == None:
        return None

    try:
        rand_numbers = random.sample(range(1, len(posts)), 5)
    except ValueError:
        rand_numbers = range(1,5)

    try: 
        rand_numbers.remove(id-1)
    except ValueError:
        rand_numbers.pop(len(rand_numbers) - 1)

    for i in rand_numbers:
        rand_posts.append(posts[i])

    return rand_posts        
