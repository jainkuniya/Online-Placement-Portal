from cloudant import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from flask import Flask, render_template, request, jsonify, redirect
import atexit
import cf_deployment_tracker
import os
import json
import string
import random
import time

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

db_name = 'mydb'
client = None
db = None
DB_DOC_LOGIN = 'login'
DB_DOC_LOGIN_FIELD_TOKEN = 'token'
DB_DOC_LOGIN_FIELD_LAST_LOGGED_IN = 'last_logged_in'
DB_DOC_LOGIN_FIELD_PASSWORD = 'password'

mis_db_name = 'mis'
mis_client = None
mis_db = None
MIS_DB_DOC_STUDENTS = 'students'
MIS_DB_DOC_STUDENTS_STUDENT_LIST = 'student_list'

SUCCESS_CODE_VALID = 1
SUCCESS_CODE_IN_VALID = 0
SUCCESS_CODE_IN_VALID_LOG_OUT = -99

DB_CONNECT_ERROR = 101
NO_RECORD_FOUND_ERROR = 102
ACCOUNT_ALREADY_EXIXT = 103

TOEKN_LENGTH = 10

def free_from_error(object):
    if object == DB_CONNECT_ERROR or object == NO_RECORD_FOUND_ERROR or object == ACCOUNT_ALREADY_EXIXT:
        return False
    else:
        return True

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# connect mis database
with open('vcap-local-mis.json') as f:
    vcap = json.load(f)
    print('Found MIS local VCAP_SERVICES')
    creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
    user = creds['username']
    password = creds['password']
    url = 'https://' + creds['host']
    mis_client = Cloudant(user, password, url=url, connect=True)
    mis_db = mis_client.create_database(mis_db_name, throw_on_exists=False)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def home():
    if 'token' in request.cookies:
        token = request.cookies['token']
        if token != '':
            return render_template('index.html')
        return redirect("./login")
    return redirect("./login")

@app.route('/login')
def login_page():
    if 'token' in request.cookies:
        token = request.cookies['token']
        if token != '':
            return redirect("./")
        else:
            return render_template('login.html')
    return render_template('login.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */

api_version = 'v1'
api_path = '/api/' + api_version +'/'

# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */

@app.route(api_path + 'fetch_from_mis', methods=['POST'])
def fetch_from_mis():
    rollNo = request.json['rollNo']
    student = get_student_details_from_mis(rollNo)
    if student == DB_CONNECT_ERROR:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Database not present",
            'data': {}
            })
    elif student == ACCOUNT_ALREADY_EXIXT:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Account already exists",
            'data': {}
            })
    elif student == NO_RECORD_FOUND_ERROR:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Invalid Roll No",
            'data': {}
            })
    else:
        return jsonify({
            'success': SUCCESS_CODE_VALID,
            'message': "Successfully retrived student",
            'data': {
                'student': student
                }
            })



def get_student_details_from_mis(rollNo):
    """Check if account already exists or not"""
    if client:
        try:
            student = db[DB_DOC_LOGIN][rollNo]
            return ACCOUNT_ALREADY_EXIXT
        except Exception, e:
            if mis_client:
                try:
                    student = mis_db[MIS_DB_DOC_STUDENTS][MIS_DB_DOC_STUDENTS_STUDENT_LIST][rollNo]
                    return student
                except Exception, e:
                    return NO_RECORD_FOUND_ERROR
            else:
                return DB_CONNECT_ERROR
    else:
        return DB_CONNECT_ERROR

@app.route(api_path + 'create_account', methods=['POST'])
def create_account():
    rollNo = request.json['rollNo']
    password = request.json['password']
    student = get_student_details_from_mis(rollNo)
    if free_from_error(student):
        """insert in out DB"""
        try:
            newEntry = db[DB_DOC_LOGIN]
            newEntry[rollNo] = {
                DB_DOC_LOGIN_FIELD_PASSWORD: password,
                DB_DOC_LOGIN_FIELD_TOKEN: '',
                DB_DOC_LOGIN_FIELD_LAST_LOGGED_IN: 0,
            }
            newEntry.save()
            return jsonify({
                'success': SUCCESS_CODE_VALID,
                'message': "Successfully registered! Please login to continue",
                })
        except Exception, e:
            print str(e)
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID,
                'message': "Please try again",
                })
    else:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Please try again",
            })

@app.route(api_path + 'login', methods=['POST'])
def login():
    rollNo = request.json['rollNo']
    password = request.json['password']
    """search in our DB"""
    try:
        student = db[DB_DOC_LOGIN]
        if student[rollNo][DB_DOC_LOGIN_FIELD_PASSWORD] == password:
            token = get_random_string(TOEKN_LENGTH)
            """Save token"""
            student[rollNo][DB_DOC_LOGIN_FIELD_PASSWORD] = password
            student[rollNo][DB_DOC_LOGIN_FIELD_TOKEN] = token
            student[rollNo][DB_DOC_LOGIN_FIELD_LAST_LOGGED_IN] = time.time()
            student.save()
            return jsonify({
                'success': SUCCESS_CODE_VALID,
                'message': "Successfully logged in",
                'data': {
                    'token': token
                }
            })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Invalid rollNo password",
            })
    except Exception as e:
        print str(e)
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "We didn't recognize you",
        })

def get_random_string(length):
    char_set = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.sample(char_set*length, length))

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
