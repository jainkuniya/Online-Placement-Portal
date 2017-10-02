from cloudant import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from flask import Flask, render_template, request, jsonify
import atexit
import cf_deployment_tracker
import os
import json
import string
import random

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

db_name = 'mydb'
client = None
db = None
DB_DOC_LOGIN = 'login'

mis_db_name = 'mis'
mis_client = None
mis_db = None
MIS_DB_DOC_STUDENTS = 'students'
MIS_DB_DOC_STUDENTS_STUDENT_LIST = 'student_list'

SUCCESS_CODE_VALID = 1
SUCCESS_CODE_IN_VALID = 0

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
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */

api_version = 'v1'
api_path = '/api/' + api_version +'/'

@app.route('/api/visitors', methods=['GET'])
def get_visitor():
    if client:
        return jsonify(list(map(lambda doc: doc['name'], db)))
    else:
        print('No database')
        return jsonify([])

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
@app.route('/api/visitors', methods=['POST'])
def put_visitor():
    user = request.json['name']
    if client:
        data = {'name':user}
        db.create_document(data)
        return 'Hello %s! I added you to the database.' % user
    else:
        print('No database')
        return 'Hello %s!' % user

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
            newEntry[rollNo] = { 'password': password }
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

def getRandomString(length):
    char_set = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.sample(char_set*length, length))

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
