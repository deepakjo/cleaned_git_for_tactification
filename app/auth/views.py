"""
All custom login and logout apis are defined here.
"""
from flask import redirect, url_for, request, session, render_template, flash, jsonify, abort
from flask_login import current_user, login_required, login_user, logout_user
from .. import db
from ..models import User, Permission, Role
from ..main.mail import send_email
from . forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from . import auth

@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        users = User.query.all()
        if user is not None and user.verify_password(form.password.data):
            if (login_user(user, remember=form.remember_me.data) is False):
                return abort(403)
            flash('Successfully logged in.')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout', methods=['GET'])
def logout():
    """
    login uses flask-oauthlib api's. But logout is defined here
    for both fb and twitter.
    """
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    r=Role.query.all()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email has been already been used.')
            return redirect(url_for('auth.login'))
        if form.email.data == 'tactification@gmail.com':
            r=Role.query.filter_by(permissions=Permission.ADMINISTER | \
                                               Permission.COMMENT | \
                                               Permission.WRITE_ARTICLES |
                                               Permission.MODERATE_COMMENTS).first()
        else:
            r=Role.query.filter_by(permissions=Permission.COMMENT).first()

        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    role=r)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
    
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_anonymous is False:
        print 'current user confirmed?', current_user.confirmed
    
    """
    Is this function used really? The indention of this api
    is to block unconfirmed users. BUt with oathlib, unconnfirmed
    option is not enabled.
    """
	#pg 120. User profile
    if current_user.is_authenticated:
        current_user.ping()

        if  not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.':
            print 'unconfirmed user'
            return redirect(url_for('auth.unconfirmed'))
        else:
            print 'confirmed user'

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_confirmation_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
            flash('An email with instructions to reset your password has been '
                  'sent to you.')
        else:
            flash('This email is not registered with us.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.confirm(token):
            user.password = form.password.data
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


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
