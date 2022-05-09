from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField,SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[
                                DataRequired(),
                                Length(min=2, max=20)
                            ])
    email = StringField('Email', 
                         validators=[
                             DataRequired(),
                             Email()
                         ])
    password = PasswordField('Password', 
                              validators=[
                                  DataRequired()
                              ])
    confirm_password = PasswordField('Confirm Password', 
                                      validators=[
                                          DataRequired(),
                                          EqualTo('password')
                                      ])
    role = SelectField ('Role',choices=[('doctor','doctor'),('patient','patient')],
                            validators=[
                                DataRequired()
                            ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('username already take!')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email already take!')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                         validators=[
                             DataRequired(),
                             Email()
                         ])
    password = PasswordField('Password', 
                              validators=[
                                  DataRequired()
                              ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class DoctorForm(FlaskForm):
    name = StringField('Name')
    is_approved = BooleanField('is_approved')
    email = TextAreaField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Post')

class PatientForm(FlaskForm):
    name = StringField('Name')
    email = TextAreaField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Post')

class AppointmentForm(FlaskForm):
    date = DateField('Appointment Date')
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add')