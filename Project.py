from flask import Flask, render_template, request, json, redirect, url_for
from flaskext.mysql import MySQL

class User:
    def __init__(self, email, password, tp):
        self.email = email
        self.password = password
        self.type = tp

    def getEmail(self):
        return self.email
        

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'carandreaf91'
app.config['MYSQL_DATABASE_DB'] = 'dbInformation'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()
cursor =conn.cursor()

@app.route("/logIn", methods = ["POST"]) #Login page for staff & student.
def logIn():
    global currentUser
    _name = request.form['email']
    _password = request.form['password']
    
    cursor.execute("SELECT * from Users")
    data = cursor.fetchall()
    for i in data:
        if (i[1] == _name and i[2] == _password):
            currentUser = User(i[1], i[2], i[3])
            if (i[3] == "A"):
                return 'Success Staff'
            else:
                return 'Success Student'
    return 'Error'

@app.route('/staffConsole') #Routeing for staff to be able to sign in.
def staffConsole():
    try:
        global currentUser
        string = "SELECT * from Staff WHERE username = '" + currentUser.getEmail() + "'"
        cursor.execute(string)
        staff = cursor.fetchone()
        data = {"user": staff[2]}
        return render_template('staffConsole.html', data=data)
    except:
        return redirect(url_for("index"))

@app.route('/studentConsole') #Routing for students to be able to sign in.
def studentConsole():
    try:
        global currentUser
        string = "SELECT * from Student WHERE username = '" + currentUser.getEmail() + "'"
        cursor.execute(string)
        data = cursor.fetchone()
        _id = data[0]
        data = {"user": data[1] + " " + data[2] + " " + data[3], "id": data[0], "birthDate":data[4], "department": data[5], "gpa": data[6]}
        
        string = """SELECT Class.class_id, Class.startDate, Class.endDate, Course.*, Offline.building, Offline.room from Register INNER JOIN Student ON Student.id = Register.student_id INNER JOIN Class ON Register.class_id = Class.class_id INNER JOIN Course ON Course.id = Class.course_id INNER JOIN Offline ON Class.class_id = Offline.class_id WHERE Student.id = %s"""
        cursor.execute(string,(_id))
        info = list(cursor.fetchall())
        string = ''
        for x in info:
            x = list(x)
            for val in x:
                string +=  str(val) + ';'
            string += "*"
        data["offline"] = string
        sql = """SELECT Class.class_id, Class.startDate, Class.endDate, Course.*, Online.url, Online.browser from Register INNER JOIN Student ON Student.id = Register.student_id INNER JOIN Class ON Register.class_id = Class.class_id INNER JOIN Course ON Course.id = Class.course_id INNER JOIN Online ON Class.class_id = Online.class_id WHERE Student.id = %s"""
        cursor.execute(sql,(_id))
        info = list(cursor.fetchall())
        string = ''
        for x in info:
            x = list(x)
            for val in x:
                string +=  str(val) + ';'
            string += "*"
        
        data["online"] = string
        return render_template('studentConsole.html', data=data)
    except:
        return redirect(url_for("index"))
        
@app.route('/Students')
def students():
    return render_template('studentsMaintain.html') #rendering student html template

@app.route("/addStudent", methods = ["POST"]) #Add student to db.
def addStudent():
    try:
        _id = request.form['studentID']
        _fn = request.form['firstName']
        _mi = request.form['middleInitial']
        _ln = request.form['lastName']
        _date = request.form['dateBirth']
        _department = request.form['department']
        _gpa = request.form['gpa']
        _username = request.form['username']
        data = (_id, _fn, _mi, _ln, _date, _department, _gpa, _username)
        cursor.execute("""INSERT INTO Student(id, firstName, middleInitial, lastName, dateOfBirth, Department, CumulativeGPA, Username) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error' 
    
@app.route("/findStudent", methods = ["POST"]) #Find existing student.
def findStudent():
    try:
        cursor.execute("SELECT * from Student WHERE id = " + request.form['studentID'])
        staff = cursor.fetchone()
        if (staff):
            staff = list(staff)
            staff[0] = str(staff[0])
            staff[6] = str(staff[6])
            return ';'.join(staff)
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/updateStudent", methods = ["POST"]) #Update student.
def updateStudent():
    try:
        _id = request.form['studentID']
        _fn = request.form['firstName']
        _mi = request.form['middleInitial']
        _ln = request.form['lastName']
        _date = request.form['dateBirth']
        _department = request.form['department']
        _gpa = request.form['gpa']
        _username = request.form['username']
        data = (_fn, _mi, _ln, _date, _department, _gpa, _username, _id)
        cursor.execute("""UPDATE Student SET firstName = %s, middleInitial = %s, lastName = %s, dateOfBirth = %s, Department = %s, CumulativeGPA = %s, Username = %s WHERE id = %s""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route("/deleteStudent", methods = ["POST"]) #Delete student.
def deleteStudent():
    try:
        cursor.execute("DELETE FROM Student WHERE id = " + request.form['studentID'])
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route('/Register')
def register():
    return render_template('registerStudents.html')

@app.route('/RegisterStudent', methods = ["POST"]) #Register student.
def registerStudent():
    cursor.execute("SELECT * from Register WHERE student_id = %s AND class_id = %s", (request.form['studentID'], request.form['classID']))
    courseRegistered = cursor.fetchone()
    print(courseRegistered)
    if (courseRegistered != None):
        return "Error"
    else:
        try:
            data = (request.form['studentID'], request.form['classID'])
            cursor.execute("""INSERT INTO Register (student_id, class_id) VALUES(%s, %s)""", data)
            conn.commit()
            return "Success"
        except:
            return "Error"
    return "Error"

@app.route('/listClasses', methods = ["POST"]) #List existing classes.
def listClasses():
    cursor.execute("SELECT * from Class")
    data = list(cursor.fetchall())
    if (data):
        string = ""
        for i in data:
            i = list(i)
            i[0] = str(i[0])
            string += '<tr>'
            for x in i:
                string += '<td>' + x + '</td>'
            string += '</tr>'
        print(string)
        return string
    return "Error"

@app.route('/findStudentRegister', methods = ["POST"]) #Find registered student, staff only.
def findStudentRegister():
    try:
        cursor.execute("SELECT * from Student WHERE id = " + request.form['studentID'])
        staff = cursor.fetchone()
        if (staff):
            staff = list(staff)
            staff[0] = str(staff[0])
            staff[6] = str(staff[6])
            return ' '.join(staff)
        else:
            return 'Error'
    except:
        return 'Error'

@app.route('/findCourseRegister', methods = ["POST"]) #Find course to register for
def findCourseRegister():
    try:
        cursor.execute("SELECT * from Course WHERE id = %s", (request.form['courseID']))
        staff = cursor.fetchone()
        if (staff):
            staff = list(staff)
            staff[2] = str(staff[2])
            return ' '.join(staff)
        else:
            return 'Error'
    except:
        return 'Error'


@app.route('/Courses') #find courses
def courses():
    return render_template('coursesMaintain.html')

@app.route("/addCourse", methods = ["POST"]) #add course
def addCourse():
    try:
        _id = request.form['courseID']
        _cn = request.form['courseName']
        _ch = request.form['creditHours']
        _desc = request.form['description']
        _pre = request.form['prerequisite']
        data = (_id, _cn, _ch, _desc, _pre)
        cursor.execute("""INSERT INTO Course(id, name, creditHours, description, prerequisites) VALUES (%s, %s, %s, %s, %s)""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/findCourse", methods = ["POST"]) #find course
def findCourse():
    try:
        cursor.execute("SELECT * from Course WHERE id = %s", (request.form['courseID']))
        staff = cursor.fetchone()
        if (staff):
            staff = list(staff)
            staff[2] = str(staff[2])
            return ';'.join(staff)
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/updateCourse", methods = ["POST"]) #Update course in db
def updateCourse():
    try:
        _id = request.form['courseID']
        _cn = request.form['courseName']
        _ch = request.form['creditHours']
        _desc = request.form['description']
        _pre = request.form['prerequisite']
        data = (_cn, _ch, _desc, _pre, _id)
        cursor.execute("""UPDATE Course SET name = %s, creditHours = %s, description = %s, prerequisites = %s WHERE id = %s""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route("/deleteCourse", methods = ["POST"]) #Delete course from db
def deleteCourse():
    try:
        cursor.execute("DELETE FROM Course WHERE id = %s", (request.form['courseID']))
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route('/Classes')
def classes():
    return render_template('classesMaintain.html') #render class template

@app.route("/addClass", methods = ["POST"]) #add class 
def addClass():
    try:
        _id = request.form['classID']
        _start = request.form['startDate']
        _end = request.form['endDate']
        _type = request.form['type']
        _courseID = request.form['courseID']
        
        data = (_id, _start, _end, _type, _courseID)
        cursor.execute("""INSERT INTO Class(class_id, startDate, endDate, type, course_id) VALUES (%s, %s, %s, %s, %s)""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/findClass", methods = ["POST"]) #find class
def findClass():
    try:
        cursor.execute("SELECT * from Class WHERE class_id = %s", (request.form['classID']))
        staff = cursor.fetchone()
        if (staff):
            staff = list(staff)
            staff[0] = str(staff[0])
            return ';'.join(staff)
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/updateClass", methods = ["POST"]) #update class
def updateClass():
    try:
        _id = request.form['classID']
        _start = request.form['startDate']
        _end = request.form['endDate']
        _type = request.form['type']
        _courseID = request.form['courseID']
        data = (_start, _end, _type, _courseID, _id)
        cursor.execute("""UPDATE Class SET startDate = %s, endDate = %s, course_id = %s WHERE class_id = %s""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route("/deleteClass", methods = ["POST"]) #delete class
def deleteClass():
    try:
        cursor.execute("DELETE FROM Class WHERE class_id = %s", (request.form['classID']))
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route('/Online') #render online class html
def online():
    return render_template('onlineClassesMaintain.html')

@app.route("/addOnClass", methods = ["POST"])
def addOnClass(): #add online class
    try:
        _url = request.form['url']
        _browser = request.form['browser']
        _id = request.form['classID']
        
        data = (_url, _browser, _id)
        cursor.execute("""INSERT INTO Online(url, browser, class_id) VALUES (%s, %s, %s)""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/findOnClass", methods = ["POST"])
def findOnClass(): #find online class
    try:
        cursor.execute("SELECT * from Online WHERE id = %s", (request.form['onID']))
        staff = cursor.fetchone()
        if (staff):
            staff = list(staff)
            staff[0] = str(staff[0])
            staff[3] = str(staff[3])
            return ';'.join(staff)
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/updateOnClass", methods = ["POST"])
def updateOnClass(): #update online classs
    try:
        _url = request.form['url']
        _browser = request.form['browser']
        _id = request.form['classID']
        _onID = request.form['onID']
        data = (_url, _browser, _id, _onID)
        cursor.execute("""UPDATE Online SET url = %s, browser = %s, class_id = %s WHERE id = %s""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route("/deleteOnClass", methods = ["POST"])
def deleteOnClass(): #delete online class
    try:
        cursor.execute("DELETE FROM Online WHERE id = %s", (request.form['onID']))
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route('/Offline')
def offline():
    return render_template('offlineClassesMaintain.html') #Render offline class html


@app.route("/addOffClass", methods = ["POST"]) #Add offline class
def addOffClass():
    try:
        _build = request.form['building']
        _room = request.form['room']
        _id = request.form['classID']
        
        data = (_build, _room, _id)
        cursor.execute("""INSERT INTO Offline(building, room, class_id) VALUES (%s, %s, %s)""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/findOffClass", methods = ["POST"]) #Find offline class
def findOffClass():
    try:
        cursor.execute("SELECT * from Offline WHERE id = %s", (request.form['offID']))
        staff = cursor.fetchone()
        if (staff):
            staff = list(staff)
            staff[2] = str(staff[2])
            return ';'.join(staff)
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/updateOffClass", methods = ["POST"]) #Update offline class
def updateOffClass():
    try:
        _build = request.form['building']
        _room = request.form['room']
        _id = request.form['classID']
        _offID = request.form['offID']
        data = (_build, _room, _id, _offID)
        cursor.execute("""UPDATE Offline SET building = %s, room = %s, class_id = %s WHERE id = %s""", data)
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'

@app.route("/deleteOffClass", methods = ["POST"]) #Delete offline class
def deleteOffClass():
    try:
        cursor.execute("DELETE FROM Offline WHERE id = %s", (request.form['offID']))
        conn.commit()
        if (cursor.rowcount == 1):
            return 'Success'
        else:
            return 'Error'
    except:
        return 'Error'
    
@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
