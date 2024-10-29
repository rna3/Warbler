from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField 
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """ Edit Form """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('(Optional) Bio')
    header_image_url = StringField('Header Image URL', validators=[Optional()])
    password = PasswordField('Current Password', validators=[DataRequired(), Length(min=6)])
    

class ChangePasswordForm(FlaskForm):
    """Form for changing a user's password."""
    
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired(), Length(min=6)]
    )
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message="Passwords must match.")]
    )