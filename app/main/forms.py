from wtforms import StringField, SubmitField, SelectField, TextAreaField, \
validators, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required
from flask_wtf.file import FileAllowed
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from .. import gifs

#Chapter 4: Form class
class PostForm(FlaskForm):
    header = PageDownField("Header", validators=[Required()])
    body = PageDownField("Predict the next three passes?", validators=[Required()])
    tactical_gif = FileField('Gif file', validators=[FileAllowed(gifs)])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    comment = TextAreaField('Post analysis', validators=[Required()])
    submit = SubmitField('Submit')
    
class AnonymousCommentForm(FlaskForm):
    name = StringField('Name', [validators.required(), validators.length(max=20)])
    comment = TextAreaField('Post your analysis', [validators.required()])
    submit = SubmitField('Submit')

