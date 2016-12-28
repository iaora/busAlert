from flask import render_template, redirect, request, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from alert import app, db, lm
from models import *
from urllib2 import urlopen
#from datetime import datetime, timedelta
import urllib2, urllib, json, xmltodict
from pytz import timezone
#from jinja2 import Environment

@lm.user_loader
def load_user(id):
        return Student.query.get(int(id))




@app.route('/', methods=['POST', 'GET'])
def home():
    activeBuses = actives()
    return render_template('index.html', buses=activeBuses)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name  = request.form.get('name')
        number = request.form.get('number')
        #Check to see if use exists
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

#load schedules of specific buses in JSON response
@app.route('/schedules/<bus>', methods=['GET','POST'])
def schedule(bus):
    url = 'http://runextbus.herokuapp.com/route/' + bus
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    #get time to be returned and print out estimate time
    #time = datetime.now(timezone('EST'))
    #print time.hour
    #print time.minute
    #print time + timedelta(minutes = 10)
    for i in data:
        if i == 'name':
            return render_template('schedules.html', busName=bus)
    #for i in data:
    #    print i['title']
    #    for k in i['predictions']:
    #        print k['minutes']
    return render_template('schedules.html', busName=bus, data=data)


@app.route('/profile/<number>', methods=['GET','POST'])
def profile(number):
    return render_template('index.html')


#Helper method to get predictions of a specific bus + stop
#@param: bus routeTag and bus stop name
#@returns: XML to dictionary format. Kinda annoying to traverse through
def predictions(bus, stop):
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?a=rutgers&command=predictions&r=' + bus + '&s=' + stop
    return getDict(url)


#Helper method to get API results converted from XML to dict
def getDict(url):
    file = urllib2.urlopen(url)
    data = file.read()
    file.close()

    data = xmltodict.parse(data)
    return data


#Gets list of active buses that are running via traversing through the XML->dict object (really annoying)
def actives():
    #Get bus data from API and convert from XML to dictionary
    file = urllib2.urlopen('http://webservices.nextbus.com/service/publicXMLFeed?a=rutgers&command=vehicleLocations')
    data = file.read()
    file.close()
    data = xmltodict.parse(data)

    results = data['body']['vehicle']
    activeBuses = []
    #Add each nested key into list
    for i in range(len(results)):
        activeBuses.append(results[i]['@routeTag'])
    #Remove duplicates of the list and put into alphabetic order
    activeBuses = removeDup(sorted(activeBuses))

    return activeBuses

#Removes duplicates and maintains order of a python list
def removeDup(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
