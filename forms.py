from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CommentFormWithLogin(FlaskForm):
    comment = TextAreaField('comment', validators=[DataRequired()])
    submitWithOutName = SubmitField('submitWithOutName')

class CommentFormWithName(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submitWithName = SubmitField('submitWithName')