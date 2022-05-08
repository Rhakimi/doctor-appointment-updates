import secrets
import os
from PIL import Image
from fileinput import filename
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy import null
from flaskblog import app, db, bcrypt
from flaskblog.forms import DoctorForm, RegistrationForm, LoginForm, UpdateAccountForm, AppointmentForm
from flaskblog.models import Doctor, Patient, User, Appointment
from flask_login import current_user, login_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.filter_by(is_approved=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=1)
    return render_template('home.html')
    # return render_template('home.html', posts=posts)




@app.route("/register_user", methods=['GET', 'POST'])
def register_user():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        if form.role.data == 'doctor':
            doctor = Doctor(name=form.username.data, email=form.email.data, user_id=user.id)
            db.session.add(doctor)
            db.session.commit()
        elif form.role.data == 'patient':
            patient = Patient(name=form.username.data, email=form.email.data, user_id=user.id)
            db.session.add(patient)
            db.session.commit()
        flash('your account is created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.role == 'doctor':
            doctor = Doctor.query.filter_by(email=form.email.data).first()
            if doctor.is_approved == False:
                flash('Your account  is not approved. ask your admin to validateed your account.', 'danger')
                return redirect(url_for('login'))

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessfull. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# patient routes
@app.route("/register_patient", methods=['GET', 'POST'])
def register_patient():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        patient = Patient(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(patient)
        db.session.commit()
        flash('your account is created', 'success')
        return redirect(url_for('login_patient'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login_patient", methods=['GET', 'POST'])
def login_patient():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(email=form.email.data).first()
        if patient and bcrypt.check_password_hash(patient.password, form.password.data):
            login(patient, remember=form.remember_me.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessfull. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout",)
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/appointment/new", methods=['GET', 'POST'])
@login_required
def create_appointment():
    appointments = Appointment.query.filter(Appointment.id>0).order_by(Appointment.id.desc())
    form = AppointmentForm()
    if form.validate_on_submit():
        if current_user.role == 'doctor':
            appointment = Appointment(date=form.date.data, doctor_id=current_user.id, description=form.description.data)
            db.session.add(appointment)
            db.session.commit()
            flash('Your Schedule Added!', 'success')

        else:
            appointment = Appointment.query.filter_by(date=form.date.data).first()
            appointment.patient_id = current_user.id
            db.session.add(appointment)
            db.session.commit()
            flash('Your booked the date!', 'success')
        # flash('Your booked the date!', 'success')
        return redirect(url_for('create_appointment'))
    return render_template('create_appointment.html', title='New Appointment', 
        form=form, legend='Create Appointment', appointments=appointments)

@app.route("/approvals", methods=['GET', 'POST'])
@login_required
def approvals():
    doctors = Doctor.query.all()
    form = DoctorForm()
    return render_template('approvals.html', title='New Appointment', legend='Create Appointment', form=form, doctors=doctors)

@app.route("/approve_doctor/<int:doctor_id>", methods=['GET', 'POST'])
@login_required
def approve_doctor(doctor_id):
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    doctor.is_approved = True
    db.session.commit()
    flash('doctor approved', 'success')
    return redirect(url_for('approvals'))

