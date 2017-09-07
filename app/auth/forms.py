from flask_wtf import FlaskForm
from flask_uploads import IMAGES
from flask_wtf.file import FileAllowed 
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
validators, ValidationError, TextAreaField, FileField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User
from .. import photos

class LoginForm(FlaskForm):
    email = StringField('Email', [validators.required(), validators.length(1, \
        64), validators.Email()])
    password = PasswordField('Password', [validators.required()])
    submit = SubmitField('Log In')
    rememberMe = BooleanField('Remember me')

class RegistrationForm(FlaskForm):
    email = StringField('Email', [validators.required(), validators.length(1, \
        64), validators.Email()])
    username = StringField('Username', [validators.required(), validators.length(1, \
        64), validators.Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must \
        have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(), \
        EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm Password', validators=[Required()])
    about_me = TextAreaField('About Me', validators=[Required()])
    location = StringField('Location', [validators.required(), validators.length(1,32)])
    profile_pic = FileField('Profile Picture', validators=[FileAllowed(photos)])
    submit = SubmitField('Register')

    def validate_email(self, field):
	print 'field', field
	print 'field.data', field.data
	
        if (User.query.filter_by(email=field.data).first()):
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if (User.query.filter_by(username=field.data).first()):
            raise ValidationError('Uname already in use')

class ChangePwdForm(FlaskForm):
    cur_password = PasswordField('Current Password', [validators.required()])
    new_password = PasswordField('New Password', validators=[Required(), \
        EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password', [validators.required()])
    submit = SubmitField('Submit')

class ResetPwdForm_Email(FlaskForm):
    email = StringField('Email', [validators.required(), validators.length(1, \
        64), validators.Email()])
    submit = SubmitField('Submit')

class ResetPwdForm_NewPwd(FlaskForm):
    changedPwd = PasswordField('New Password', [validators.required()])
    submit = SubmitField('Save')

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    profile_pic = FileField('Profile Picture', validators=[FileAllowed(photos, 'Image only!')])
    submit = SubmitField('Submit')
