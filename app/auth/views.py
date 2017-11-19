"""
All custom login and logout apis are defined here.
"""
from flask import redirect, url_for, request, session
from flask_login import current_user, login_required, logout_user
from . import auth

@auth.route('/logout/<post_id>', methods=['GET'])
def logout(post_id):
    """
    login uses flask-oauthlib api's. But logout is defined here
    for both fb and twitter.
    """
    logout_user()
    if post_id == '-1':
        return redirect(url_for('main.index'))

    return redirect(url_for('main.post', id=post_id))

@auth.before_app_request
def before_request():
    """
    Is this function used really? The indention of this api
    is to block unconfirmed users. BUt with oathlib, unconnfirmed
    option is not enabled.
    """
	#pg 120. User profile
    if current_user.is_authenticated:
        current_user.ping()

    if current_user.is_authenticated \
        and not current_user.confirmed \
        and (request.endpoint is None and request.endpoint[:5] != 'auth.'):
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/session_info')
@login_required
def user_session_info():
    """
    session details only for debugging purpose.
    """
    print 'session_details', session
    print 'type(current_user)', type(current_user.email)
    print 'current_user', current_user.email
    return redirect(url_for('main.index'))
