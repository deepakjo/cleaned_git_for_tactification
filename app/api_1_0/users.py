from flask import jsonify
from . import api_rt
from ..models import Post, Permission, User, Comment
from decorators import admin_required, permission_required
from flask_login import login_required

@api_rt.route('/user/<username>')
@login_required
@admin_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)

    return jsonify(user.to_json())

@api_rt.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.last_seen.asc()).all()
    if users is None:
        abort(404)

    return jsonify({'users': [user.to_json() for user in users],
                    'no_of_users': len(users)})
