import datetime
from typing import Optional
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from sqlalchemy import DATE, DateTime
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField,SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from appointment_system.models import Schedule, User

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

    specialization = StringField('Specialization')
    
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('username already take!')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email already take!')
    
    def validate_specialization(self, specialization):
        if (self.role.data == 'doctor'):
            if (specialization.data == ''):
                raise ValidationError('specialization can not be empty!')

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

class CreateSchedule(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()], default= datetime.date.today() )
    end_date = DateField('End Date', validators=[DataRequired()])
    title = TextAreaField('Title', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data:
            raise ValidationError("Please choose a proper date!")
    
    def validate_start_date(self, start_date):
        if start_date.data < datetime.date.today():
            raise ValidationError("Please choose a proper date!")

 
  

class MakeAppointment(FlaskForm):
    doctor_id= HiddenField('doctor_id')
    schedule_id= HiddenField('schedule_id')
    reason = TextAreaField('Reason', validators=[DataRequired()])
    date = DateField('Select Date', validators=[DataRequired()])
    submit = SubmitField('submit')

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

class UpdateSchedule(FlaskForm):
    start_date = DateField('Update Start Date', validators=[DataRequired()], default= datetime.date.today() )
    end_date = DateField('Update End Date', validators=[DataRequired()])
    title = TextAreaField('Update Title', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data:
            raise ValidationError("Please choose a proper date!")
    
    def validate_start_date(self, start_date):
        if start_date.data < datetime.date.today():
            raise ValidationError("Please choose a proper date!")
