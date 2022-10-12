from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField
from wtforms.validators import DataRequired, Email, NumberRange, Length
from flask_ckeditor import CKEditorField


##WTForm
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In")


class RatingForm(FlaskForm):
    rating = FloatField('Your rating out of 10 e.g. 7.5:', validators=[NumberRange(min=0, max=10)])
    review = StringField('Your review (max 30 char):', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Submit')


class AddForm(FlaskForm):
    title = StringField('Movie title', validators=[DataRequired()])
    submit = SubmitField('Search')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = FloatField('Phone', validators=[DataRequired()])
    message = CKEditorField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
