from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, SelectField


class UserForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired(), validators.Length(min=4, max=64)])
    password = PasswordField('Password', validators=[validators.DataRequired(), validators.Length(min=4, max=32)])
    submit = SubmitField('Submit')


class AdminUserForm(UserForm):
    role = SelectField('Choose role', choices=[], coerce=int)