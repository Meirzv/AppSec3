from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, optional
from app.models import LoginUser


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=1, max=15)])
    mfa = StringField("2FA - Phone Number", validators=[optional()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=1, max=15)])
    mfa = StringField("2FA - Phone Number", validators=[optional()])
    submit = SubmitField("Register Now")

    def validate_username(self, username):
        user = LoginUser.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is already taken! Please use a different Username.')


class SpellChecker(FlaskForm):
    command = StringField('Spell check words input', validators=[DataRequired()])
    submit = SubmitField("Go!")

class HistoryAdmin(FlaskForm):
    username = StringField('Enter a username', validators=[DataRequired()])
    submit = SubmitField("submit")