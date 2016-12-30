from alert import app, db
from flask.ext.login import UserMixin


class Classes(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    courseNum = db.Column(db.String(15), nullable=False)
    sectionNum = db.Column(db.String(2), nullable=False)
    startTime = db.Column(db.String(4), nullable=False)
    endTime = db.Column(db.String(4), nullable=False)
    pm = db.Column(db.String(1), nullable=False)
    meetingDay = db.Column(db.String(3), nullable=False)
    campus = db.Column(db.String(10), nullable=False)
    building = db.Column(db.String(20), nullable=False)

class Student(db.Model, UserMixin):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name =  db.Column(db.String(25), nullable=False)
    number = db.Column(db.String(12), unique=True, nullable=False)


class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    classID = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    busStop = db.Column(db.String(15), nullable=False)
    bus = db.Column(db.String(2), db.ForeignKey('busses.name'), nullable=False)


class Bus(db.Model):
    __tablename__ = 'busses'
    id = db.Column(db.Integer,)
    name = db.Column(db.String(2), primary_key=True, unique=True)

