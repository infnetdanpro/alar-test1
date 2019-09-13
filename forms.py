from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, SelectField
from wtforms.validators import InputRequired, Length


class UserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message='This field is required!'), Length(min=4, max=64, message='min 4, max 64')])
    password = PasswordField('Password', validators={InputRequired(message='This field is required!'), Length(min=4, max=32, message='min 4, max 32')})
    submit = SubmitField('Submit')


class AdminUserForm(UserForm):
    role = SelectField('Choose role', choices=[], coerce=int)