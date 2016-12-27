from flask import render_template, redirect, request, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from alert import app, db, lm
from models import *
from urllib2 import urlopen

@lm.user_loader
def load_user(id):
        return Student.query.get(int(id))


@app.route('/', methods=['POST', 'GET'])
def home():

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name  = request.form.get('name')
        number = request.form.get('number')
        if request.form.get('login_or_signup') == 'signup': #signup
            user = Student.query.filter_by(number=number).first()
            if user is not None:
                return "number already exists.. pls no"
            user = Student(name=name, number=number)
            db.session.add(user)
            db.session.commit()
            login_user(user, True)
            print "user successfully added"
            return redirect(url_for('home'))

        else: #login
            user = Student.query.filter_by(number=number).first()
            if user is None:
                return "user doesnt exist"

            login_user(user, True)
            print "user successfully logged in"
            return redirect(url_for('home'))



@app.route('/profile', methods=['GET','POST'])
def profile():
    return render_template('index.html')


@app.route('/active', methods=['GET'])
def activebuses():
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
