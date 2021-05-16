from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
from bson import json_util
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions

# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
        
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")


    if users.find({"username":f"{data['username']}"}).count() == 0 :
        users.insert({"username":f"{data['username']}", "password":f"{data['password']}"})
        return Response(data['username']+" was added to the MongoDB", mimetype='application/json', status=200) 
    else:
        return Response("A user with the given email already exists", mimetype='application/json', status=400)  
    

# ΕΡΩΤΗΜΑ 2: Login στο σύστημα
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    
    if (users.find({"username":f"{data['username']}","password":f"{data['password']}"}).count() == 1): 
        user_uuid=create_session(data['username'])
        res = {"uuid": user_uuid, "username": data['username']}
        return Response(json.dumps(res), mimetype='application/json', status=200) 

    else:
        return Response("Wrong username or password.",mimetype='application/json', status=400) 

# ΕΡΩΤΗΜΑ 3: Επιστροφή φοιτητή βάσει email 
@app.route('/getStudent', methods=['GET'])
def get_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   
    uuid = request.headers.get('authorization')

    if is_session_valid(uuid):
        
        studentcursor = students.find_one({"email" : f"{data['email']}"})
        student = json.loads(json_util.dumps(studentcursor))
        

        if (student):

            return Response(json.dumps(student), status=200, mimetype='application/json')
        else:
            return Response("Student not found", status=400, mimetype="application/json")
    else:
        return Response("Not authorized", status=401, mimetype='application/json')


# ΕΡΩΤΗΜΑ 4: Επιστροφή όλων των φοιτητών που είναι 30 ετών
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirty():
   

    thirtiescursor = students.find({"yearOfBirth": 1991})
    Students = json.loads(json_util.dumps(thirtiescursor))


    uuid = request.headers.get('authorization')
    if is_session_valid(uuid):

        
        if Students:
            return Response(json_util.dumps(Students), status=200, mimetype='application/json')
        else:
            return Response("No students found.", status=400, mimetype="application/json")
    else:
        return Response("Not authorized", status=401, mimetype='application/json')


# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_oldies():
  
    oldiescursor = students.find({"yearOfBirth": {'$lte' : 1991}})
    Students = json.loads(json_util.dumps(oldiescursor))


    uuid = request.headers.get('authorization')
    if is_session_valid(uuid):

        
        if Students:
            return Response(json_util.dumps(Students), status=200, mimetype='application/json')
        else:
            return Response("No students found.", status=400, mimetype="application/json")
    else:
        return Response("Not authorized", status=401, mimetype='application/json')

# ΕΡΩΤΗΜΑ 6: Επιστροφή φοιτητή που έχει δηλώσει κατοικία βάσει email 
@app.route('/getStudentAddress', methods=['GET'])
def get_studentAddress():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")



    uuid = request.headers.get('authorization')
    if is_session_valid(uuid):
        addresscursor = students.find_one({"email" : f"{data['email']}", "address": {"$exists": 1}})
        addressdict = json.loads(json_util.dumps(addresscursor))



        if addressdict:
            
            student = {
                "name" : addressdict['name'],
                "street": addressdict['address'][0]['street'],
                "postcode": addressdict['address'][0]['postcode']
            }
            
            return Response(json.dumps(student), status=200, mimetype='application/json')
        else:
            return Response("No student found", status=400, mimetype="application/json")
    else:
        return Response("Not authorized", status=401, mimetype='application/json')

# ΕΡΩΤΗΜΑ 7: Διαγραφή φοιτητή βάσει email 
@app.route('/deleteStudent', methods=['DELETE'])
def delete_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   
    uuid = request.headers.get('authorization')
    if is_session_valid(uuid):
        
        delcursor = students.find_one({"email" : f"{data['email']}"})
        deldict = json.loads(json_util.dumps(delcursor))
        
        if deldict:
            students.delete_one({"email" : f"{data['email']}"})
            msg = deldict['name'] + "was deleted."
            return Response(msg, status=200, mimetype='application/json')
        else:
            msg = "Student not found"
            return Response(msg, status=400, mimetype="application/json")
    else:
        return Response("Not authorized", status=401, mimetype='application/json')

    
# ΕΡΩΤΗΜΑ 8: Εισαγωγή μαθημάτων σε φοιτητή βάσει email 
@app.route('/addCourses', methods=['PATCH'])
def add_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "courses" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   
    uuid = request.headers.get('authorization')

    if is_session_valid(uuid):
     
        courses = data['courses']

        query = {"email": f"{data['email']}"}
        newvalues = { "$set": { "courses": f"{courses}" } }

        if (students.find({"email" : f"{data['email']}"}).count()==1):
            students.update_one(query, newvalues)
            return Response("Courses added succesfully", status=200, mimetype='application/json')
        else:
            return Response("Student not found", status=400, mimetype="application/json")
    else:
        return Response("Not authorized", status=401, mimetype='application/json')
    
# ΕΡΩΤΗΜΑ 9: Επιστροφή περασμένων μαθημάτων φοιτητή βάσει email
@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   


    uuid = request.headers.get('authorization')
    if is_session_valid(uuid):
            coursescursor = students.find_one({"email" : f"{data['email']}", "courses": {"$exists": 1}})
            coursesdict = json.loads(json_util.dumps(coursescursor))

            student = {}




            if coursesdict:
                student = coursesdict['courses']
                return Response(json.dumps(student), status=200, mimetype='application/json')
            else:
                return Response("No student found", status=400, mimetype="application/json")
    else:
        return Response("Not authorized", status=401, mimetype='application/json')



# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)