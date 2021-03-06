from flask import render_template, redirect, request, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from alert import app, db, lm
from models import *
from urllib2 import urlopen
from datetime import datetime, timedelta
import urllib2, urllib, json, xmltodict
from pytz import timezone
#from jinja2 import Environment

#Loader to user for authorizing log in. Need this up here or else it would give some weird error because try to use Student before it's made or something
@lm.user_loader
def load_user(id):
        return Student.query.get(int(id))




@app.route('/', methods=['POST', 'GET'])
def home():
    activeBuses = actives()
    stops = BusStop.query
    classes = Classes.query
    msg = ''

    if request.method == 'POST':
        #Get front-end fields
        #Split '198:111.40' into '198:111' and '40' to query the Classes object to get the unique ID of that item
        bus = request.form.get('bus')
        course = request.form.get('classID')
        timePref = request.form.get('time')
        stop = request.form.get('stop')

        if 'Select' in bus or 'Select' in course or 'Select' in timePref or 'Select' in bus:
            print "ERROR IN FIELD"
            return render_template('index.html', error='Error! You forgot to select 1 or more fields', classes=classes, stops=stops, buses=activeBuses)
            

        
        #Split values to be used later
        course = course.split('.')
        timePref = timePref.split(' ')

        #Get the ID of the that specific class
        classID = Classes.query.filter_by(courseNum=course[0], sectionNum=course[1]).first()

        #Get bus ID
        stop = BusStop.query.filter_by(name=stop).first().id

        #Calculate time for alert to ring
        #Add PM or AM depending on when the class starts
        time = classID.startTime+'PM' if classID.pm == 'P' else classID.startTime+'AM'
        #Convert String->datetime obj
        timeObj = datetime.strptime(time, '%I%M%p')
        #Subtract timePref from time class starts
        newTime = timeObj - timedelta(minutes=int(timePref[0]))
        #Convert time back to a string
        newTime_string = newTime.strftime('%H%M')



        #Create new object to add and commit to DB
        new_alert = Schedule(student=current_user.id, classID=classID.id, timePref=newTime_string, bus=bus, stop=stop)
        db.session.add(new_alert)
        db.session.commit()
        msg = 'Successfully added alert :)'

    return render_template('index.html', msg=msg, classes=classes, stops=stops, buses=activeBuses)


#Method to preload the DB with buses, stops, and courses. Only need to be done once per semester. This should be its own python file.. but import errors :( I'll fix it soon
def loadDB():
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?a=rutgers&command=routeConfig'
    data = getDict(url)
    loadBuses(data)
    loadStops(data)
    loadSOC()


def loadBuses(data):
    for route in data['body']['route']:
        #Add all busses to the Bus table
        print route['@title']
        print route['@tag']

        #Create new bus object to add into DB
        bus = Bus(name=route['@tag'], running='F')
        db.session.add(bus)
        db.session.commit()

#Add all stops to the BusStop table
def loadStops(data):
    for route in data['body']['route']:
        bus = Bus.query.filter_by(name=route['@tag']).first()
        print bus
        for stop in route['stop']:
            busstop = BusStop(name=stop['@tag'], bus=bus.name)
            db.session.add(busstop)
            db.session.commit()



def loadSOC():
    url = 'http://sis.rutgers.edu/soc/courses.json?subject=198&semester=12017&campus=NB&level=U'
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    for course in data:
        courseNum = '198:' + course['courseNumber']
        for section in course['sections']:
            sectionNum = section['number']
            for info in section['meetingTimes']:
                building = info['buildingCode']
                campus = info['campusName']
                startTime = info['startTime']
                endTime = info['endTime']
                meetingDay = info['meetingDay']
                pm = info['pmCode']
                if courseNum is None or sectionNum is None or building is None or campus is None or startTime is None or endTime is None or meetingDay is None or pm is None:
                    continue
                newClass = Classes(courseNum=courseNum, sectionNum=sectionNum, startTime=startTime, endTime=endTime, pm=pm, meetingDay=meetingDay, campus=campus, building=building)
                db.session.add(newClass)
                db.session.commit()
                print "added" + courseNum + ":" + sectionNum



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
@app.route('/schedules/<bus>', methods=['GET'])
def schedule(bus):
    if request.method == 'GET':
        url = 'http://runextbus.herokuapp.com/route/' + bus
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        #wtf does this do again
        for i in data:
            if i == 'name':
                return render_template('schedules.html', busName=bus)
        #for i in data:
        #    print i['title']
        #    for k in i['predictions']:
        #        print k['minutes']
        return render_template('schedules.html', busName=bus, data=data)


#Profile route to edit schedules
@app.route('/u/<number>', methods=['GET', 'POST'])
def prof(number):
    if request.method == 'GET':
        person = Student.query.filter_by(number=number).first()
        #if person's profile is not in the DB/invalid number
        if person is None:
            print 'Person is none'
            return render_template('profile.html', number=number,  msg='This phone number does not exist')
        
        list_of_schedules = Schedule.query.filter_by(student=person.id).all()
        #if person does not have any schedules saved yet
        if list_of_schedules is None or not list_of_schedules:
            print 'Schedule is none'
            return render_template('profile.html', number=number, msg='You currently have no schedules saved')

        #Send schedule to front end to be displayed
        print 'LOL WHY'
        return render_template('profile.html', Classes=Classes, number=number, schedules=list_of_schedules)
    if request.method == 'POST':
        return render_template('profile.html')



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

    #update DB to switch running flag to T if it's in the activeBuses list. Else, set the running flag to F
    for u in Bus.query: #Query all bus objects from Bus table (!!! SO COOL)
        if u.name in activeBuses:
            #print '      ' + u.name
            u.running = 'T'
            db.session.commit()
        else:
            u.running = 'F'

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
