from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField

from wtforms.validators import InputRequired,Email
class MyRegisterForm(FlaskForm):
    username=StringField('username', validators=[InputRequired()])
    email=EmailField(
        'Email',
        validators=[InputRequired(), Email()]
    )
    Password=PasswordField('password', validators=[InputRequired()])
    confirmPassword=PasswordField('ConfirmPassword', validators=[InputRequired()])