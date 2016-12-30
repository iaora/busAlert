import urllib, json
import MySQLdb
from alert import app, db, models

def main():
    #conn = MySQLdb.connect(host= "localhost",
    #                user="alert",
    #                passwd="alert",
    #                db="alert")
    #x = conn.cursor()
    print "test"
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

                newClass = Classes(courseNum, sectionNum, startTime, endTime, pm, meetingDay, campus, building)
                db.session.add(newClass)
                db.session.commit()

                #x.execute("""INSERT INTO classes VALUES (%s,%s,%s, %s, %s, %s, %s, %s)""",(courseNum, sectionNum, startTime, endTime, pm, meetingDay, campus, building))
                print "added" + courseNum + ":" + sectionNum
                #conn.commit()

    #conn.close()

