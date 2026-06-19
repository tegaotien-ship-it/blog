from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField

from wtforms.validators import InputRequired,Email
class MyRegisterForm(FlaskForm):
    name=StringField('name', validators=[InputRequired()])
    email=EmailField(
        'Email',
        validators=[InputRequired(), Email()]
    )
    password=PasswordField('password', validators=[InputRequired()])
    confirm_password=PasswordField('confirm_password', validators=[InputRequired()])