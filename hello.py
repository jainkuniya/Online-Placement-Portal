from cloudant import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from flask import Flask, render_template, request, jsonify
import atexit
import cf_deployment_tracker
import os
import json

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

db_name = 'mydb'
client = None
db = None

mis_db_name = 'mis'
mis_client = None
mis_db = None
MIS_DB_DOC_STUDENTS = 'students'
MIS_DB_DOC_STUDENTS_STUDENT_LIST = 'student_list'

SUCCESS_CODE_VALID = 1
SUCCESS_CODE_IN_VALID = 0

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
    if mis_client:
        """Search in MIS database"""
        try:
            student = mis_db[MIS_DB_DOC_STUDENTS][MIS_DB_DOC_STUDENTS_STUDENT_LIST][rollNo]
            return jsonify({
                'success': SUCCESS_CODE_VALID,
                'message': "Successfully retrived student",
                'data': {
                    'student': student
                    }
                })
        except:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID,
                'message': "Invalid Roll No",
                'data': {}
                })
    else:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Database not present",
            'data': {}
            })

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
