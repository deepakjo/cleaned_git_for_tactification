from flask import current_app, url_for, redirect, flash, session
from flask_login import current_user
from .models import OAuthSignIn
from urllib import urlretrieve
from . import oauth_rt
from ..models import User, Role
from .. import db
from flask_login import login_user
from .. import photos

def prepend_provider_in_uid(provider, user_id):
    if (provider == 'facebook'):
        user_id = user_id + 'fb'
    elif (provider == 'twitter'):
        user_id = user_id + 'tw'

    print 'provider', provider
    print 'user_id', user_id
    return user_id

@oauth_rt.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    user_id, username, pic_url = oauth.authorize_response()
    print 'email=%s uname=%s' % (user_id, username)
    if user_id is None:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))
    user_id = prepend_provider_in_uid(provider, user_id)
    user = User.query.filter_by(email=user_id).first()
    if not user:
        urlretrieve(pic_url, current_app.config['UPLOADED_PHOTOS_DEST'] + '/' + user_id )
        filename = user_id
        file_url = photos.url(filename)        
        print 'filename=%s and file_url=%s' %(filename, file_url)
        user_role = Role.query.filter_by(permissions=0x1).first()
        print 'user_role:', user_role
        user = User(email=user_id, username=username, profile_pic = filename, role=user_role,
                    profile_url = file_url, confirmed = True, via_oauth = True)
        db.session.add(user)
        db.session.commit()

    login_user(user, force=True)
    post_id = session.get('post_id', -1)
    print 'post_id=', post_id
    try:
        session.pop('post_id')
    except KeyError:
        return redirect(url_for('main.index'))
   
    if post_id == '-1':
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.post', id=post_id))


@oauth_rt.route('/authorize/<provider>/<post_id>')
def oauth_authorize(provider, post_id):
    print 'provider=', provider
    print 'post_id=', post_id
    if not current_user.is_anonymous:
        if post_id == '-1':
            return redirect(url_for('main.index'))
        else:
            return redirect(url_for('main.post', id=post_id))

    session['post_id'] = post_id
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()
