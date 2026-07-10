from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length,Email,EqualTo
from flask import FlaskForm

class RequestResetForm(FlaskForm):
      email=StringField("Email",validators=[DataRequired(),Email()])
      submit=SubmitField("Request Password Reset")
    #   if email does not exist
      def validate_email(self,email):
          user=User.query.filter_by(email=email.data).first()
          if user:
              raise ValidationError("There is no account with that email,you must register first.")

class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField(
    'Confirm Password', 
    validators=[DataRequired(), EqualTo('password', message='Passwords must match.')] # ⬅️ Pass 'password' here
)


    submit=SubmitField( "Reset Password")