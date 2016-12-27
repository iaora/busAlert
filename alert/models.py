from alert import app, db
from flask.ext.login import UserMixin


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    courseNum = db.Column(db.String(15), unique=True, nullable=False)
    One = db.Column(db.DateTime, nullable=False)
    Two = db.Column(db.DateTime, nullable=False)
    Three = db.Column(db.DateTime, nullable=False)
    recitation = db.Column(db.DateTime, nullable=False)


class Student(db.Model, UserMixin):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name =  db.Column(db.String(25), nullable=False)
    number = db.Column(db.String(12), unique=True, nullable=False)


class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    classID = db.Column(db.String(15), db.ForeignKey('classes.courseNum'), nullable=False)
    busStop = db.Column(db.String(15), nullable=False)
    bus = db.Column(db.String(2), db.ForeignKey('busses.name'), nullable=False)


class Bus(db.Model):
    __tablename__ = 'busses'
    id = db.Column(db.Integer,)
    name = db.Column(db.String(2), primary_key=True, unique=True)

