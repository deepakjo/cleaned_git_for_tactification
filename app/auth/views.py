from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user 
from . import auth
from datetime import datetime
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePwdForm, EditProfileForm
from .forms import ResetPwdForm_Email, ResetPwdForm_NewPwd
from .. import db
from flask_login import current_user, login_required
from ..email import send_email
from urlparse import urlparse
from ..utils import allowed_file
from werkzeug.utils import secure_filename            
from .. import photos


	
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and \
            user.verify_password(form.password.data):
			session['uname'] = user.username
			login_user(user, remember=form.rememberMe.data, force=True)
			return redirect(request.args.get('next') or url_for('main.index'))

        flash('Invalid username or password:')

    return render_template('auth/login.html', form=form, current_time=datetime.utcnow())

@auth.route('/logout/<post_id>', methods=['GET'])
def logout(post_id):
    logout_user()
    if post_id == '-1':
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.post', id=post_id))

@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
	form = ChangePwdForm()
	if form.validate_on_submit():
		u = User.query.filter_by(username=session.get('uname')).first()
		u.password = form.new_password.data
		flash('New password is set')
		db.session.commit()
		return redirect(url_for('auth.logout', post_id=-1))

	return render_template('auth/change_password.html', form=form, \
		current_time=datetime.utcnow(), method=request.method)

@auth.route('/reset_pwd', methods=['GET', 'POST'])
def reset_pwd():
	form = ResetPwdForm_Email()

	if request.method == 'POST' and form.validate_on_submit():
		u = User.query.filter_by(email = form.email.data).first()

		session['email'] = form.email.data 
		if u is None:
			session['registered_user'] = False
			return redirect(url_for('auth/reset_pwd'))

		session['password_updated'] = False 
		token = u.generate_confirmation_token()
		send_email(u.email, 'Reset your password', 'auth/email/password_reset', \
			user=u, token=token)
		return redirect(url_for('auth.reset_pwd'))

	return render_template('auth/reset_password.html', form=form, \
		registered = session.get('registered_user'), username = session.get('email'),
		method=request.method, current_time=datetime.utcnow()) 
		
			 
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    print 'methodsss', form.validate_on_submit()
    if form.validate_on_submit():
        if 'profile_pic' in request.files:
            filename = photos.save(form.profile_pic.data)
            file_url = photos.url(filename)
        else:
            file_url = None 
    
        u = User(email = form.email.data, username = form.username.data, \
                 password = form.password.data, location=form.location.data, \
                 about_me = form.about_me.data, profile_pic = filename,
                 profile_url = file_url)

        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        session['email'] = form.email.data
        session['uname'] = form.username.data
        session['passwd'] = form.password.data
        #send_email(u.email, 'Confirm your account', 'auth/email/confirm', \
        #     user=u, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index')) 

    return render_template('auth/register.html', form=form, \
        email=session.get('email'), uname=session.get('uname'), \
        passwd=session.get('passwd'), method=request.method)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks')
	else:
		flash('The confirmation link is expired or incorrect')

	return redirect(url_for('main.index'))

@auth.route('/change_pwd/email/<token>', methods=['GET', 'POST'])
def reset_pwd_entering_phase(token):
	form = ResetPwdForm_NewPwd()
	if form.validate_on_submit():
			
		user = User.query.filter_by(email= session.get('email')).first()
		print user.username
		user.password = form.changedPwd.data
		db.session.commit()
		session['username'] = user.username
		session['password_updated'] = True 
		return redirect(url_for('auth.reset_pwd_entering_phase', token=token))

	return render_template('auth/reset_pwd_entering_phase.html', form=form, username=session.get('username'), password_updated = session.get('password_updated'), \
		method=request.method, current_time=datetime.utcnow()) 
		
@auth.before_app_request
def before_request():
	#pg 120. User profile
    if current_user.is_authenticated:
        current_user.ping()

    if current_user.is_authenticated \
        and not current_user.confirmed \
        and (request.endpoint == None and request.endpoint[:5] != 'auth.'):
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')	
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect('main.index')
	return render_template('auth/unconfirmed.html')
			
@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	#send_email(current_user.email, 'Confirm your Account', 'auth/email/confirm', user=current_user, token=token)
	flash('A new confirmation email has been sent to you in email.')
	return redirect(url_for('main.index'))
		
@auth.route('/session_info')
@login_required
def user_session_info():
	print 'session_details', session
	print 'type(current_user)', type(current_user.email)
	print 'current_user', current_user.email
	return redirect(url_for('main.index'))

@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        if 'profile_pic' in request.files:
            current_user.profile_pic = photos.save(form.profile_pic.data)
            current_user.profile_url = photos.url(current_user.profile_pic)
        else:
            file_url = None 
    
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))

    form.name.data = current_user.name  
    form.location.data = current_user.location 
    form.about_me.data = current_user.about_me 

    return render_template('auth/edit_profile.html', form=form, current_time=datetime.utcnow(), method=request.method) 

