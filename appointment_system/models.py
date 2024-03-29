from datetime import datetime
from email.policy import default
from appointment_system import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String(20), nullable=False)
    doctor = db.relationship('Doctor', backref='doctor', lazy=True)
    patient = db.relationship('Patient', backref='patient', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    appointment = db.relationship('Appointment', backref='doctor', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    schedule = db.relationship('Schedule', backref='doctor')

    def __repr__(self):
        return f"('{self.name}', '{self.email}')"

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    appointment = db.relationship('Appointment', backref='patient', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Patient('{self.id}', '{self.name}', '{self.email}')"

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    title = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date(), default = datetime.now().date())
    end_date = db.Column(db.Date(), default = datetime.now().date())
    appointment = db.relationship('Appointment', backref='Schedule', lazy=True)

    def __repr__(self):
        return f"('{self.title}', '{self.start_date}', '{self.end_date}')"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date= db.Column(db.Date)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    description = db.Column(db.String(100), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)

    def __repr__(self):
        return f"Appointment('{self.date}', '{self.doctor_id}', '{self.patient_id}', '{self.description}')"
