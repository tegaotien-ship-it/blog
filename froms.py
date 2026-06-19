from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DecimalField, RadioField, SelectField, TextAreaField, FileField, SubmitField
from wtforms.validators import InputRequired

class signUpfrom(FlaskForm):
    username=StringField('username',validators=[InputRequired()])
    password=PasswordField('password',validators=[InputRequired()])
    remember_me= BooleanField('Remember me')
    salary=DecimalField('Salary',validators=[InputRequired()])
    gender=RadioField('Gender',choices=[('male','Male'),('female','female')])
    country=SelectField('Country',choices=[('IN','India'),('US','United States'),('UK','United Kingdom')])
    message=TextAreaField('Message',validators=[InputRequired()])
    photo=FileField('Photo')
    submit=SubmitField('sign up')