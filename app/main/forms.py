from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError, validators

class BlogCreateForm(FlaskForm):
    header = StringField('Header', [validators.Length(min=1, max=255)])
    desc = TextAreaField('Description', [validators.Length(min=1, max=500)])
    body = TextAreaField('Body', [validators.Length(min=1)], render_kw={'rows': 400, 'cols': 81})
    twTag = StringField('Tweet Tags', [validators.Length(min=1, max=255)])
    tags = StringField('Tags', [validators.Length(min=1, max=255)])
    photo = FileField('Image File', validators=[FileRequired()])
    submit = SubmitField('Submit')

class BlogFileUploadForm(FlaskForm):
    photo = FileField('Image File', validators=[FileRequired()])
    submit = SubmitField('Submit')
    
