from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_login import login_user
from .errors import forbidden, unauthorized
from . import api_rt
from ..models import User, AnonymousUser

auth_rest = HTTPBasicAuth()

@auth_rest.error_handler
def auth_error():
	return unauthorized('Invalid credentials')

@api_rt.before_request
@auth_rest.login_required
def before_request():
    is_anonymous = getattr(g, 'is_anonymous', None)
    if is_anonymous is None:
		return forbidden('Anonymous account')

@auth_rest.verify_password
def verify_password(email_or_token, password):
    """
        :type email_or_token: str
        :type password: str
    """
    if email_or_token == '':
        g.current_user = AnonymousUser()
        g.is_anonymous = True
        return True
            
    if password == '':
        id = User.verify_auth_token(email_or_token)
        if id is None:
            return jsonify({'authentication' : 'fail'})
            
        user = User.query.filter_by(email=id).first()  
        g.current_user = user
        g.is_anonymous = False
        g.token_used = True
        login_user(user, force=True)
        return g.current_user is not None
            
    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return False
            
    g.current_user = user
    g.is_anonymous = False
    g.token_used = False
    login_user(g.current_user, force=True)
    return user.verify_password(password)

@api_rt.route('/token')
def get_token():
    is_anonymous = getattr(g, 'is_anonymous', None)
    is_token_used = getattr(g, 'token_used', None)
    if is_anonymous is None or is_token_used is None:
        return unauthorized('Invalid credentials')
	
    return jsonify({'token':g.current_user.generate_auth_token(expiration=3600),
                        'expiration':3600})
                        
        
