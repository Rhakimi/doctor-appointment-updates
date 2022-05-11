from ast import Pass
import secrets
import os
from PIL import Image
from fileinput import filename
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy import and_
from appointment_system import app, db, bcrypt
from appointment_system.forms import DoctorForm, MakeAppointment, RegistrationForm, LoginForm, AppointmentForm, CreateSchedule
from appointment_system.models import Doctor, Patient, User, Appointment, Schedule
from flask_login import current_user, login_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    doctors = Doctor.query.all()
    # posts = Post.query.filter_by(is_approved=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=1)
    
    return render_template('home.html', doctors=doctors)
    # return render_template('home.html', posts=posts)

@app.route("/doctor/schedule/<int:id>")
def doctor_schedule(id):
    doctor = Doctor.query.filter_by(id=id).first()
    return render_template('doctor_schedule.html', schedules=doctor.schedule)


@app.route("/create/schedule", methods=['GET', 'POST'])
def create_schedule():
    form = CreateSchedule()
    schedules = Schedule.query.filter_by(doctor_id=current_user.id).all()
    if form.validate_on_submit():
        
        new_schedule= Schedule(title=form.title.data, doctor_id=current_user.id, start_date=form.start_date.data,
                                end_date=form.end_date.data)
        db.session.add(new_schedule)
        db.session.commit()
        return redirect(url_for('create_schedule'))
    return render_template('create_schedule.html', form=form, schedules=schedules)

@app.route("/view/doctor/schedule/<int:id>")
def view_doctor_schedule(id):
    schedules = Schedule.query.filter_by(doctor_id=id).all()
    return render_template('view_doctor_schedules.html', schedules=schedules)


@app.route("/create/appointment/<int:id>", methods=['GET', 'POST'])
def patient_create_appointment(id):
    form = MakeAppointment()
    form.doctor_id.data = id
    form.schedule_id.data = request.args.get('schedule_id')
    if form.validate_on_submit():
        desired_schedule = Schedule.query.filter_by(id=form.schedule_id.data).first()
        incoming_date_exist = db.session.query(Appointment)\
            .filter(and_(Appointment.schedule_id == form.schedule_id.data,
                         Appointment.date == form.date.data)).all()
        if incoming_date_exist:
            flash("this date booked before please choose a different one!", 'info')
            return render_template('book_appointment.html', form=form)
        if form.date.data >= desired_schedule.start_date and form.date.data <= desired_schedule.end_date:
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            new_appintment = Appointment(date=form.date.data, schedule_id=form.schedule_id.data,
                                        doctor_id=form.doctor_id.data, description=form.reason.data, patient_id= patient.id)
            db.session.add(new_appintment)
            db.session.commit()
            flash("Your appointment booked successfully!", 'success')
            return redirect(url_for('view_doctor_schedule', id=id))
        flash('Please choose correct Date!', 'info')
    return render_template('book_appointment.html', form=form)

@app.route("/view/booked/appointment")
def user_view_appointment():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    print(patient)
    my_appointment = db.session.query(Appointment.date, Appointment.description, Doctor.name, Doctor.email)\
                    .join(Doctor, Doctor.id==Appointment.doctor_id).filter(Appointment.patient_id==patient.id).all()
    return render_template('my_appointment.html', appointments=my_appointment)

@app.route("/view/booked/patients")
def booked_patients():
    
    # patients = db.session.query(Appointment.date, Appointment.description, Patient.name, Patient.email).join(Patient, Appointment.patient_id==Patient.id).filter(Appointment.doctor_id==current_user.id).all()
    # patients = db.session.query(Appointment.date, Appointment.description, Patient.name, Patient.email).filter(Appointment.doctor_id==current_user.id).all()
    patients = db.session.query(Appointment.date, Appointment.description, Patient.name, Patient.email).join(Patient, Appointment.patient_id==Patient.id).filter(Appointment.doctor_id==current_user.id).all()
    print("---------------",patients)
    # print("---------------",patients)
    return render_template('view_booked_patients.html', patients=patients)



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
            flash('your account is created, Kindly Wait For admin approval', 'success')

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
        if not user:
            flash('your Email or Password is incorrect!', 'warning')
            return render_template('login.html', form=form)
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
    print("---",appointments)
    form = AppointmentForm()
    if form.validate_on_submit():
        if current_user.role == 'doctor':
            print("---", dir(current_user))
            appointment = Appointment(date=form.date.data, doctor_id=current_user.doctor[0].id, description=form.description.data)
            db.session.add(appointment)
            db.session.commit()
            flash('Your Schedule Added!', 'success')

        else:
            appointment = Appointment.query.filter_by(date=form.date.data).first()
            if appointment:
                if appointment.patient_id:
                    flash('Sorry Date Has already been booked !', 'success')
                    return redirect(url_for('create_appointment'))
                else:
                    appointment.patient_id = current_user.patient[0].id
                    db.session.add(appointment)
                    db.session.commit()
                    flash('Your booked the date!', 'success')
            else:
                flash('Sorry No Appointment Available On the Date Selected !', 'success')
                return redirect(url_for('create_appointment'))
        # flash('Your booked the date!', 'success')
        return redirect(url_for('create_appointment'))
    return render_template('create_appointment.html', title='New Appointment', 
        form=form, legend='Create Appointment', appointments=appointments)

@app.route("/approvals", methods=['GET', 'POST'])
@login_required
def approvals():
    doctors = Doctor.query.all()
    form = DoctorForm()
    return render_template('approvals.html', title='New Appointment', legend='Create Appointment', doctors=doctors)

@app.route("/approve_doctor/<int:doctor_id>", methods=['GET', 'POST'])
@login_required
def approve_doctor(doctor_id):
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    doctor.is_approved = True
    db.session.commit()
    flash('doctor approved', 'success')
    return redirect(url_for('approvals'))

