import cloudant
from cloudant import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from flask import Flask, render_template, request, jsonify, redirect, make_response
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

DB_DOC_TYPE = 'doc_type'
DB_DOC_FIELD_ROLL_NO = 'roll_no'

DB_DOC_LOGIN = 'login'
DB_DOC_LOGIN_FIELD_TOKEN = 'token'
DB_DOC_LOGIN_FIELD_LAST_LOGGED_IN = 'last_logged_in'
DB_DOC_LOGIN_FIELD_PASSWORD = 'password'

DB_DOC_STUDENT_BASIC = 'student_basic'
DB_DOC_STUDENT_ACADEMIC = 'student_academic'
DB_DOC_STUDENT_FAMILY_DETAILS = 'student_family'
DB_DOC_STUDENT_PROJECTS = 'projects'
DB_DOC_STUDENT_EXPRIENCES = 'expriences'

DB_DOC_STUDENT_BASIC_FIELD_PROGRAM = "program"
DB_DOC_STUDENT_BASIC_FIELD_BRANCH = "branch"
DB_DOC_STUDENT_BASIC_FIELD_ADMISSION_YEAR = "addmission_year"

DB_DOC_RECUITER = "recuiter"
DB_DOC_FEEDBACK = "feedback"

DB_DOC_APPLY = "apply"

DB_DOC_NOTIFICATION = "notifications"

mis_db_name = 'mis'
mis_client = None
mis_db = None

MIS_DB_DOC_STUDENTS = 'students'
MIS_DB_DOC_STUDENTS_STUDENT_LIST = 'student_list'
MIS_DB_DOC_STUDENTS_STUDENT_LIST_BASIC = 'basic'
MIS_DB_DOC_STUDENTS_STUDENT_LIST_ACADEMIC = 'academic'

MIS_DB_DOC_FIELD_PROGRAM = "program"
MIS_DB_DOC_FIELD_BRANCH = "branch"
MIS_DB_DOC_FIELD_ADMISSION_YEAR = "addmission_year"

SUCCESS_CODE_VALID = 1
SUCCESS_CODE_IN_VALID = 0
SUCCESS_CODE_IN_VALID_LOG_OUT = -99

INVALID_TOKEN = -99

DB_CONNECT_ERROR = 101
NO_RECORD_FOUND_ERROR = 102
ACCOUNT_ALREADY_EXIXT = 103

TOEKN_LENGTH = 10

REQUIRED_ADMISSION_YEAR = 14
NOT_FINAL_YEAR = 3

TPO_USER_NAME = "TPO"

def free_from_error(object):
    if object == DB_CONNECT_ERROR or object == NO_RECORD_FOUND_ERROR or object == ACCOUNT_ALREADY_EXIXT or object == INVALID_TOKEN or object == NOT_FINAL_YEAR:
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

def fetch_student_basic_details(token):
    """check if token is valid or not"""
    status = verify_token(token)
    if free_from_error(status):
        """get basic details"""
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_STUDENT_BASIC,
                                 DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                            }
            )
        result = query(limit=100)['docs']
        if (len(result) == 1):
            return result[0]
        else:
            return NO_RECORD_FOUND_ERROR
    else:
        return INVALID_TOKEN

def fetch_student_academic_details(rollNo):
    #"""check if token is valid or not"""
    #status = verify_token(token)
    #if free_from_error(status):
    """get basic details"""
    query = cloudant.query.Query(
        db, selector = {
                             DB_DOC_TYPE: DB_DOC_STUDENT_ACADEMIC,
                             DB_DOC_FIELD_ROLL_NO: rollNo,
                        }
        )
    result = query(limit=100)['docs']
    if (len(result) == 1):
        return result[0]
    else:
        return NO_RECORD_FOUND_ERROR
    #else:
    #    return INVALID_TOKEN

def fetch_student_family_details(rollNo):
    #"""check if token is valid or not"""
    #status = verify_token(token)
    #if free_from_error(status):
    """get basic details"""
    query = cloudant.query.Query(
        db, selector = {
                             DB_DOC_TYPE: DB_DOC_STUDENT_FAMILY_DETAILS,
                             DB_DOC_FIELD_ROLL_NO: rollNo,
                        }
        )
    result = query(limit=100)['docs']
    if (len(result) == 1):
        return result[0]
    else:
        return NO_RECORD_FOUND_ERROR
    #else:
    #    return INVALID_TOKEN

def fetch_student_project(rollNo):
    #"""check if token is valid or not"""
    #status = verify_token(token)
    #if free_from_error(status):
    """fetch_student_project"""
    query = cloudant.query.Query(
        db, selector = {
                             DB_DOC_TYPE: DB_DOC_STUDENT_PROJECTS,
                             DB_DOC_FIELD_ROLL_NO: rollNo,
                        }
        )
    result = query(limit=100)['docs']
    if (len(result) == 1):
        return result[0]
    else:
        return NO_RECORD_FOUND_ERROR
    #else:
    #    return INVALID_TOKEN

def fetch_student_expriences(rollNo):
    #"""check if token is valid or not"""
    #status = verify_token(token)
    #if free_from_error(status):
    """fetch_student_expriences"""
    query = cloudant.query.Query(
        db, selector = {
                             DB_DOC_TYPE: DB_DOC_STUDENT_EXPRIENCES,
                             DB_DOC_FIELD_ROLL_NO: rollNo,
                        }
        )
    result = query(limit=100)['docs']
    if (len(result) == 1):
        return result[0]
    else:
        return NO_RECORD_FOUND_ERROR
    #else:
    #    return INVALID_TOKEN

def verify_token(token):
    query = cloudant.query.Query(
        db, selector = {
                             DB_DOC_TYPE: DB_DOC_LOGIN,
                             DB_DOC_LOGIN_FIELD_TOKEN: token,
                        }
        )
    result = query(limit=100)['docs']
    if (len(result) == 1):
        return result[0]
    else:
        return INVALID_TOKEN

@app.route('/logout')
def logout():
    resp = make_response(render_template('login.html'))
    resp.set_cookie('token', expires=0)
    return resp

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
            'message': "Invalid credentials",
            'data': {}
            })
    elif (student == NOT_FINAL_YEAR):
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "You are not in final year.",
            })
    else:
        return jsonify({
            'success': SUCCESS_CODE_VALID,
            'message': "Successfully retrived student",
            'data': {
                'student': student
                }
            })


def get_student_from_our_db(rollNo, password):
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_LOGIN,
                                 DB_DOC_FIELD_ROLL_NO: rollNo,
                                 'password': password
                            }
            )
        result = query(limit=100)['docs']
        if (len(result) == 1):
            return result[0]
        else:
            return NO_RECORD_FOUND_ERROR

    else:
        return DB_CONNECT_ERROR


def get_student_details_from_mis(rollNo):
    """Check if account already exists or not"""
    student = get_student_from_our_db(rollNo, -1)
    if (student == NO_RECORD_FOUND_ERROR):
        if mis_client:
            try:
                mis_db[MIS_DB_DOC_STUDENTS].fetch()
                student = mis_db[MIS_DB_DOC_STUDENTS][MIS_DB_DOC_STUDENTS_STUDENT_LIST][rollNo]
                if (student["addmission_year"] == REQUIRED_ADMISSION_YEAR):
                    return student
                else:
                    return NOT_FINAL_YEAR
            except Exception, e:
                return NO_RECORD_FOUND_ERROR
        else:
            return DB_CONNECT_ERROR
    elif (student == DB_CONNECT_ERROR):
        return DB_CONNECT_ERROR
    else:
        return ACCOUNT_ALREADY_EXIXT

@app.route(api_path + 'tpo/create_recuiter', methods=['POST'])
def create_recuiter():
    if 'token' in request.cookies:
        token = request.cookies['token']
        """if (free_from_error(verify_token(token))):"""
        companyName = request.json['company_name']
        password = get_random_string(5)
        userId = get_random_string(5)
        try:
            data = {
                DB_DOC_TYPE: DB_DOC_LOGIN,
                'companyName': companyName,
                DB_DOC_FIELD_ROLL_NO: userId,
                DB_DOC_LOGIN_FIELD_PASSWORD: password,
                DB_DOC_LOGIN_FIELD_TOKEN: '',
                DB_DOC_LOGIN_FIELD_LAST_LOGGED_IN: 0,
                'person_type': 2,
            }
            db.create_document(data)
            print data
            data = {
                DB_DOC_TYPE: DB_DOC_RECUITER,
                'companyName': companyName,
                DB_DOC_FIELD_ROLL_NO: userId,
                'verified': 0,
                'positions': {},
                'schedule': {},
            }
            db.create_document(data)
            print data
            return jsonify({
                'success': SUCCESS_CODE_VALID,
                'message': "Successfully created",
                'password': password,
                'userId': userId,
                })
        except Exception, e:
            print str(e)
            print "vishwesh"
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID,
                'message': "Please try again",
                })
        """return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Please try again",
            })"""
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please login again",
        })

def create_notification(roll_no, message):
    try:
        data = {
            DB_DOC_TYPE: DB_DOC_NOTIFICATION,
            'to': roll_no,
            'message': message,
        }
        db.create_document(data)

        return 1
    except Exception, e:
        print str(e)
        return 0

@app.route(api_path + 'recuiter/feedback', methods=['POST'])
def recuiter_feedback():
    if 'token' in request.cookies:
        token = request.cookies['token']
        recuiter = verify_token(token)
        if (free_from_error(recuiter)):
            try:
                """create a new doc of type login"""
                data = {
                    DB_DOC_TYPE: DB_DOC_FEEDBACK,
                    DB_DOC_FIELD_ROLL_NO: recuiter[DB_DOC_FIELD_ROLL_NO],
                    'feedback': request.json['feedback'],
                }
                db.create_document(data)

                create_notification(TPO_USER_NAME, "New Feedback from recuiter")

                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully registered! Please login to continue",
                    })
            except Exception, e:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                    })
        else:
            jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please login again!",
                })
    else:
        jsonify({
            'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
            'message': "Please login again!",
            })


@app.route(api_path + 'create_account', methods=['POST'])
def create_account():
    rollNo = request.json['rollNo']
    password = request.json['password']
    student = get_student_details_from_mis(rollNo)
    if free_from_error(student):
        """insert in our DB"""
        try:
            """create a new doc of type login"""
            data = {
                DB_DOC_TYPE: DB_DOC_LOGIN,
                DB_DOC_FIELD_ROLL_NO: rollNo,
                DB_DOC_LOGIN_FIELD_PASSWORD: password,
                DB_DOC_LOGIN_FIELD_TOKEN: '',
                DB_DOC_LOGIN_FIELD_LAST_LOGGED_IN: 0,
                'person_type': 1,
            }
            db.create_document(data)

            """create a doc of type student_basic"""
            data = {
                DB_DOC_TYPE: DB_DOC_STUDENT_BASIC,
                DB_DOC_FIELD_ROLL_NO: rollNo,
                DB_DOC_STUDENT_BASIC_FIELD_PROGRAM: student[MIS_DB_DOC_FIELD_PROGRAM],
                DB_DOC_STUDENT_BASIC_FIELD_BRANCH: student[MIS_DB_DOC_FIELD_BRANCH],
                DB_DOC_STUDENT_BASIC_FIELD_ADMISSION_YEAR: student[MIS_DB_DOC_FIELD_ADMISSION_YEAR],
                'verified': 0
            }
            data.update(student[MIS_DB_DOC_STUDENTS_STUDENT_LIST_BASIC])
            db.create_document(data)

            """create a doc of type student_academic"""
            data = {
                DB_DOC_TYPE: DB_DOC_STUDENT_ACADEMIC,
                DB_DOC_FIELD_ROLL_NO: rollNo,
            }
            data.update(student[MIS_DB_DOC_STUDENTS_STUDENT_LIST_ACADEMIC])
            db.create_document(data)

            create_notification(TPO_USER_NAME, "New student to verify: " + rollNo)

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
    elif (student == NOT_FINAL_YEAR):
        jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "You are not in final year!",
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
    student = get_student_from_our_db(rollNo, password)
    if free_from_error(student):
        """Save token"""
        try:
            token = get_random_string(TOEKN_LENGTH)
            db[student["_id"]].fetch()
            doc = db[student["_id"]]
            doc[DB_DOC_LOGIN_FIELD_TOKEN] = token
            doc[DB_DOC_LOGIN_FIELD_LAST_LOGGED_IN] = time.time()
            doc.save()
            return jsonify({
                'success': SUCCESS_CODE_VALID,
                'message': "Successfully logged in",
                'data': {
                    'person_type': doc['person_type'],
                    'token': token
                }
            })
        except Exception as e:
            print e
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID,
                'message': "Please try again",
            })

    else:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Invalid credentials",
        })

def get_random_string(length):
    char_set = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.sample(char_set*length, length))

def get_templete(page_name):
    if 'token' in request.cookies:
        token = request.cookies['token']
        if token != '':
            basic_details = fetch_student_basic_details(token)
            if (free_from_error(basic_details)):
                notifications = get_notifications(basic_details[DB_DOC_FIELD_ROLL_NO])
                if (page_name == "family"):
                    family_details = fetch_student_family_details(basic_details[DB_DOC_FIELD_ROLL_NO])
                    return render_template('family.html', notifications=notifications, basic_details= basic_details, family_details= family_details, page=page_name)
                elif (page_name == "academic"):
                    academic_details = fetch_student_academic_details(basic_details[DB_DOC_FIELD_ROLL_NO])
                    return render_template('academic.html', notifications=notifications, basic_details= basic_details, academic_details= academic_details, page=page_name)
                elif (page_name == "projects"):
                    projects = fetch_student_project(basic_details[DB_DOC_FIELD_ROLL_NO])
                    return render_template('projects.html', notifications=notifications, basic_details= basic_details, projects=projects, page=page_name)
                elif (page_name == "exprience"):
                    expriences = fetch_student_expriences(basic_details[DB_DOC_FIELD_ROLL_NO])
                    return render_template('exprience.html', notifications=notifications, basic_details= basic_details, expriences=expriences, page=page_name)
                elif (page_name == "companies"):
                    positions = fetch_positions(basic_details[DB_DOC_FIELD_ROLL_NO], basic_details[DB_DOC_STUDENT_BASIC_FIELD_BRANCH])
                    return render_template('students_positions.html', notifications=notifications, basic_details= basic_details, positions= positions, page=page_name)
                else:
                    return render_template('index.html', notifications=notifications, basic_details= basic_details, page=page_name)
            else:
                """invalid token, redirect to logout"""
                return redirect("./logout")
        return redirect("./login")
    return redirect("./login")

def get_applied_candidate(cCode):
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_APPLY,
                                 'valid': 1,
                                 'c_code': cCode,
                                 'selected': 0,
                            }
            )
        result = query(limit=100)['docs']
        return result
    else:
        return []

def get_recuiter_selected_candidate(cCode):
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_APPLY,
                                 'valid': 1,
                                 'c_code': cCode,
                                 'selected': 1,
                            }
            )
        result = query(limit=100)['docs']
        return result
    else:
        return []

def get_notifications(roll_no):
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_NOTIFICATION,
                                 'to': roll_no,
                            }
            )
        result = query(limit=100)['docs']
        return result
    else:
        return []

def get_status(roll_no, code):
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_APPLY,
                                 'valid': 1,
                                 DB_DOC_FIELD_ROLL_NO: roll_no,
                                 'p_code': code,
                            }
            )
        result = query(limit=100)['docs']
        if (len(result) == 1):
            if (result[0]["selected"] == 1):
                return "Selected!!"
            return "applied"
        return "can_apply"

    else:
        return "can_apply"

def fetch_positions(roll_no, branch):
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_RECUITER,
                                 'verified': 1,
                            }
            )
        data = []
        result = query(limit=100)['docs']
        for com in result:
            if "positions" in com:
                positions = []
                for po in com["positions"]:
                    """check if already applied"""
                    if (com["positions"][po] != -1):
                        positions.append({
                            'position': com["positions"][po],
                            'status': get_status(roll_no, po),
                            'code': po,
                        })
                    time.sleep(0.5)
                data.append({
                    'companyName': com["companyName"],
                    'companyCode': com["roll_no"],
                    'positions': positions,
                })
            else:
                data.append({
                    'companyName': com["companyName"],
                    'companyCode': com["roll_no"],
                    'positions': {},
                })
        return data

    else:
        return []

@app.route(api_path + 'apply_for_position', methods=['POST'])
def apply_for_position():
    if 'token' in request.cookies:
        token = request.cookies['token']
        basic = verify_token(token)
        if (free_from_error(basic)):
            try:
                data = {
                    DB_DOC_TYPE: DB_DOC_APPLY,
                    'c_code': request.json["cCode"],
                    'c_name': request.json["cName"],
                    'p_code': request.json["pCode"],
                    DB_DOC_FIELD_ROLL_NO: basic[DB_DOC_FIELD_ROLL_NO],
                    'selected': 0,
                    'valid': 1,
                }
                db.create_document(data)

                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully created",
                    })
            except Exception, e:
                print str(e)
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                    })
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please login again",
        })

def get_tpo_templete(page_name):
    if 'token' in request.cookies:
        token = request.cookies['token']
        if token != '':
            notifications = get_notifications("TPO")
            if (page_name == "tpo_students"):
                pending_students = get_pending_students()
                all_verified_students = get_all_verified_students()
                return render_template('tpo_students.html', notifications=notifications, pending_students=pending_students, all_verified_students=all_verified_students, page_name=page_name)
            elif (page_name == "tpo_recruiter_cred"):
                return render_template('tpo_recruiter_cred.html', notifications=notifications, page_name=page_name)
            elif (page_name == "tpo_recruiter_verify"):
                pending_recuiter = get_pending_recuiters()
                all_recuiter = get_all_verified_recuiters()
                return render_template('tpo_recruiter_verify.html', notifications=notifications, pending_recuiter=pending_recuiter, all_recuiter=all_recuiter, page_name=page_name)
            elif (page_name == "tpo_analysis"):
                analysis = get_placement_analysis()
                return render_template('tpo_analysis.html', analysis=analysis, notifications=notifications, page_name=page_name)
            elif (page_name == "feedback"):
                feedbacks = get_feedbacks()
                return render_template('tpo_feedback.html', feedbacks=feedbacks, notifications=notifications, page_name=page_name)
            else:
                return redirect("./logout")
        return redirect("./logout")
    return redirect("./logout")

@app.route('/')
def home():
    if 'token' in request.cookies:
        token = request.cookies['token']
        if token != '':
            person = verify_token(token)
            if (free_from_error(person)):
                print person["person_type"]
                if (person["person_type"] == 1):
                    return get_templete("home")
                elif (person["person_type"] == 0):
                    return get_tpo_templete("tpo_students")
                elif (person["person_type"] == 2):
                    return get_recuiter_templete("event_details")
                else:
                    return redirect("./logout")
            else:
                return redirect("./logout")
        else:
            return redirect("./logout")
    else:
        return redirect("./logout")

@app.route('/family')
def family_page():
    return get_templete("family")

@app.route('/academic')
def academic_page():
    return get_templete("academic")

@app.route('/projects')
def projects_page():
    return get_templete("projects")

@app.route('/exprience')
def exprience_page():
    return get_templete("exprience")

@app.route('/companies')
def companies():
    return get_templete("companies")

@app.route('/tpo')
def tpo_students_page():
    return get_tpo_templete("tpo_students")

@app.route('/tpo_recruiter_cred')
def tpo_reccred_page():
    return get_tpo_templete("tpo_recruiter_cred")

@app.route('/tpo_recruiter_verify')
def tpo_recverify_page():
    return get_tpo_templete("tpo_recruiter_verify")

@app.route('/tpo_analysis')
def tpo_analysis_page():
    return get_tpo_templete("tpo_analysis")

@app.route('/feedback')
def tpo_feedback_page():
    return get_tpo_templete("feedback")

@app.route('/event')
def get_recuiter_templete(page_name):
    if 'token' in request.cookies:
        token = request.cookies['token']
        if token != '':
            details = fetch_recuiter(token)
            if (free_from_error(details)):
                notifications = get_notifications(details[DB_DOC_FIELD_ROLL_NO])
                if (page_name == "event_details"):
                    return render_template('event_details.html', notifications=notifications, details= details, page=page_name)
                elif (page_name == "position_details"):
                    return render_template('position_details.html', notifications=notifications, details= details, page=page_name)
                elif (page_name == "schedule"):
                    return render_template('schedule.html', notifications=notifications, details= details, page=page_name)
                elif (page_name == "reg_details"):
                    return render_template('reg_details.html', notifications=notifications, details= details, page=page_name)
                elif (page_name == "offers"):
                    applied_candidates = get_applied_candidate(details[DB_DOC_FIELD_ROLL_NO])
                    selected_candidate = get_recuiter_selected_candidate(details[DB_DOC_FIELD_ROLL_NO])
                    return render_template('offers.html', details= details, applied_candidates=applied_candidates, selected_candidate=selected_candidate, page=page_name)
                elif(page_name == "feedback"):
                    return render_template('feedback.html', notifications=notifications, details= details, page=page_name)
                else:
                    return redirect("./logout")
            else:
                """invalid token, redirect to logout"""
                return redirect("./logout")
        return redirect("./login")
    return redirect("./login")

@app.route('/recuiter')
def event_details():
    return get_recuiter_templete('event_details')

@app.route('/recuiter/position_details')
def position_details():
    return get_recuiter_templete('position_details')

@app.route('/recuiter/schedule')
def schedule_details():
    return get_recuiter_templete('schedule')

@app.route('/recuiter/reg_details')
def registration_details():
    return get_recuiter_templete('reg_details')

@app.route('/recuiter/offers')
def offers_details():
    return get_recuiter_templete('offers')

@app.route('/recuiter/feedback')
def feedback_details():
    return get_recuiter_templete('feedback')

@app.route(api_path + 'tpo/verify_student', methods=['POST'])
def verify_student():
    status = verify_individual_student(request.json['rollNo'])
    if free_from_error(status):
        return jsonify({
            'success': SUCCESS_CODE_VALID,
            'message': "Successfully verified",
        })
    else:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID,
            'message': "Please try again",
        })

@app.route(api_path + 'tpo/verify_all_student', methods=['POST'])
def verify_all_student():
    pending_students = get_pending_students()
    if (request.json["whichGroup"] == 0):
        for student in pending_students["noBacklog"]:
            verify_individual_student(student['rollNo'])
    else:
        for student in pending_students["backlog"]:
            verify_individual_student(student['rollNo'])
    return jsonify({
        'success': SUCCESS_CODE_VALID,
        'message': "Successfully verified",
    })

def verify_individual_student(rollNo):
    query = cloudant.query.Query(
        db, selector = {
                             DB_DOC_TYPE: DB_DOC_STUDENT_BASIC,
                             DB_DOC_FIELD_ROLL_NO: rollNo,
                        }
        )
    result = query(limit=100)['docs']
    if (len(result) == 1):
        doc = db[result[0]['_id']]
        doc.fetch()
        doc['verified'] = 1

        doc.save()

        create_notification(rollNo, "Your account is verified! ")

        return doc
    else:
        return NO_RECORD_FOUND_ERROR

@app.route(api_path + 'tpo/approve_recuiter', methods=['POST'])
def approve_recuiter():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: request.json["id"],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                doc['verified'] = 1

                doc.save()

                """send notification to all verified students"""
                send_notification_to_all_verified_students("New company is listed! ")

                create_notification(doc[DB_DOC_FIELD_ROLL_NO], "Your account is verified by TPO, positions are visible to students.")

                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully verified",
                    })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "No recuiter found",
                    })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please login again",
                })
    else:
        return jsonify({
            'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
            'message': "Please login again",
            })

def get_all_verified_students():
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_STUDENT_BASIC,
                                 'verified': 1,
                            }
            )
        result = query(limit=100)['docs']
        students = []
        return result

    else:
        return []

def get_placement_analysis():
    registered_students_count = len(get_all_verified_students())
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_APPLY,
                                 'selected': 1,
                            }
            )
        result = query(limit=100)['docs']
        average_package = 0
        highest_package = 0
        lowest_package = 999999999999
        for offer in result:

            average_package = (average_package + int(offer["package"]))
            if int(offer["package"]) > highest_package:
                highest_package = int(offer["package"])
            if int(offer["package"]) < lowest_package:
                lowest_package = int(offer["package"])

        if (len(result) == 0):
            lowest_package = 0
        else:
            average_package = average_package / len(result)

        return {
            'selected_students': result,
            'selected_students_count': len(result),
            'registered_students_count': registered_students_count,
            'unplaced_students_count': registered_students_count - len(result),
            'package': {
                'highest': highest_package,
                'average': average_package,
                'lowest': lowest_package,
            },
        }

    else:
        return {}


def send_notification_to_all_verified_students(message):
    students = get_all_verified_students()
    for student in students:
        create_notification(student[DB_DOC_FIELD_ROLL_NO], message)

    return 1

def get_all_verified_recuiters():
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_RECUITER,
                                 'verified': 1,
                            }
            )
        result = query(limit=100)['docs']
        return result

    else:
        return DB_CONNECT_ERROR

def get_feedbacks():
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_FEEDBACK,
                            }
            )
        result = query(limit=100)['docs']
        return result

    else:
        return DB_CONNECT_ERROR

def get_pending_recuiters():
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_RECUITER,
                                 'verified': 0,
                            }
            )
        result = query(limit=100)['docs']
        return result

    else:
        return DB_CONNECT_ERROR

def fetch_recuiter(token):
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_LOGIN,
                                 'person_type': 2,
                                 'token': token
                            }
            )
        result = query(limit=100)['docs']
        if (len(result) == 1):
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: result[0][DB_DOC_FIELD_ROLL_NO]
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                return result[0]
            else:
                return NO_RECORD_FOUND_ERROR

        else:
            return NO_RECORD_FOUND_ERROR

    else:
        return DB_CONNECT_ERROR

def get_pending_students():
    if client:
        query = cloudant.query.Query(
            db, selector = {
                                 DB_DOC_TYPE: DB_DOC_STUDENT_BASIC,
                                 'verified': 0,
                            }
            )
        result = query(limit=100)['docs']
        noBacklog = []
        backlog = []
        for student in result:
            """get backlog"""
            acad_query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_ACADEMIC,
                                     DB_DOC_FIELD_ROLL_NO: student[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            acad_result = acad_query(limit=100)['docs']
            time.sleep(0.5)
            if (len(acad_result) == 1):
                if (len(acad_result[0]['active_backlog'].keys()) == 0):
                    noBacklog.append({
                        'rollNo': student[DB_DOC_FIELD_ROLL_NO],
                        'name': student['first_name'] + " " + student['last_name'],
                        'backlog': acad_result[0]['active_backlog']
                    })
                else:
                    backlog.append({
                        'rollNo': student[DB_DOC_FIELD_ROLL_NO],
                        'name': student['first_name'] + " " + student['last_name'],
                        'backlog': acad_result[0]['active_backlog']
                    })
        return {
            'backlog': backlog,
            'noBacklog': noBacklog
        }

    else:
        return DB_CONNECT_ERROR

@app.route(api_path + 'recuiter/reg_details', methods=['POST'])
def update_reg_details():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_event_details"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                doc['start_date'] = request.json['start_date']
                doc['start_time'] = request.json['start_time']
                doc['end_date'] = request.json['end_date']
                doc['end_time'] = request.json['end_time']
                doc['reg_details_other_details'] = request.json['reg_details_other_details']

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'recuiter/select_candidate', methods=['POST'])
def select_candidate():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """select candidate"""
            query = cloudant.query.Query(
                db, selector = {
                                     '_id': request.json["id"],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                doc['selected'] = 1
                doc['position'] = request.json['position']
                doc['package'] = request.json['package']

                doc.save()
                create_notification(doc['roll_no'], "Congrats!! Selected for " + request.json['position'] + ", package " + request.json['package'])

                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })


@app.route(api_path + 'recuiter/create_position', methods=['POST'])
def create_position():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """create_position"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                position_id = get_random_string(5)
                doc['positions'][position_id] = {}
                doc['positions'][position_id]['title'] = request.json['title']
                doc['positions'][position_id]['type'] = request.json['type']
                doc['positions'][position_id]['position_type'] = request.json['position_type']
                doc['positions'][position_id]['description'] = request.json['description']
                doc['positions'][position_id]['job_other_details'] = request.json['job_other_details']
                doc['positions'][position_id]['location'] = request.json['location']
                doc['positions'][position_id]['joining_date'] = request.json['joining_date']
                doc['positions'][position_id]['ctc'] = request.json['ctc']
                doc['positions'][position_id]['fixed_gross'] = request.json['fixed_gross']
                doc['positions'][position_id]['bonus_name'] = request.json['bonus_name']
                doc['positions'][position_id]['bonus_amount'] = request.json['bonus_amount']

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'recuiter/create_schedule', methods=['POST'])
def create_schedule():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """create_schedule"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                schedule_id = get_random_string(5)
                doc['schedule'][schedule_id] = {}
                doc['schedule'][schedule_id]['agenda'] = request.json['agenda']
                doc['schedule'][schedule_id]['date'] = request.json['date']
                doc['schedule'][schedule_id]['time'] = request.json['time']
                doc['schedule'][schedule_id]['venue'] = request.json['venue']
                doc['schedule'][schedule_id]['details'] = request.json['details']

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })


@app.route(api_path + 'recuiter/event_details', methods=['POST'])
def update_event_details():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_event_details"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                doc['eventTitle'] = request.json['event_title']
                doc['companyName'] = request.json['company_name']
                doc['type'] = request.json['type']
                doc['eligibility_criteria'] = request.json['eligibility_criteria']
                doc['selection_process_details'] = request.json['selection_process_details']
                doc['other_details'] = request.json['other_details']
                doc['cce'] = request.json['cce']
                doc['cse'] = request.json['cse']
                doc['ece'] = request.json['ece']
                doc['mme'] = request.json['mme']
                doc['me'] = request.json['me']

                doc.save()
                print "vishwesh"
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                print "vishwesh 2"
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            print "vishwesh 3"
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'update_basic_details', methods=['POST'])
def update_basic_details():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_basic_details"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_BASIC,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                doc['first_name'] = request.json['first_name']
                doc['last_name'] = request.json['last_name']
                doc['gender'] = request.json['gender']
                doc['date_of_birth'] = request.json['date_of_birth']
                doc['email'] = request.json['email']
                doc['phone_number'] = request.json['phone_number']
                doc['address'] = request.json['address']

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'update_academic_details', methods=['POST'])
def update_academic_details():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_academic_details"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_ACADEMIC,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                doc['12_institute'] = request.json['12_institute']
                doc['12_city'] = request.json['12_city']
                doc['12_country'] = request.json['12_country']
                doc['12_board'] = request.json['12_board']
                doc['12_year'] = request.json['12_year']
                doc['12_aggregate'] = request.json['12_aggregate']
                doc['12_subjects'] = request.json['12_subjects']
                doc['10_institute'] = request.json['10_institute']
                doc['10_city'] = request.json['10_city']
                doc['10_country'] = request.json['10_country']
                doc['10_board'] = request.json['10_board']
                doc['10_year'] = request.json['10_year']
                doc['10_aggregate'] = request.json['10_aggregate']
                doc['10_subjects'] = request.json['10_subjects']

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'update_family_details', methods=['POST'])
def update_family_details():
    print request.json
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_family_details"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_FAMILY_DETAILS,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                """doc exists"""
                doc = db[result[0]['_id']]
                doc.fetch()
                doc['father_name'] = request.json['father_name']
                doc['father_occupation'] = request.json['father_occupation']
                doc['father_company'] = request.json['father_company']
                doc['father_designation'] = request.json['father_designation']
                doc['father_email'] = request.json['father_email']
                doc['father_phone_number'] = request.json['father_phone_number']
                doc['mother_name'] = request.json['mother_name']
                doc['mother_occupation'] = request.json['mother_occupation']
                doc['mother_company'] = request.json['mother_company']
                doc['mother_designation'] = request.json['mother_designation']
                doc['mother_email'] = request.json['mother_email']
                doc['mother_phone_number'] = request.json['mother_phone_number']

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            elif (len(result) == 0):
                """create doc"""
                data = {
                    DB_DOC_TYPE: DB_DOC_STUDENT_FAMILY_DETAILS,
                    DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                    'father_name' :  request.json['father_name'],
                    'father_occupation' :  request.json['father_occupation'],
                    'father_company' :  request.json['father_company'],
                    'father_designation' :  request.json['father_designation'],
                    'father_email' :  request.json['father_email'],
                    'father_phone_number' :  request.json['father_phone_number'],
                    'mother_name' :  request.json['mother_name'],
                    'mother_occupation' :  request.json['mother_occupation'],
                    'mother_company' :  request.json['mother_company'],
                    'mother_designation' :  request.json['mother_designation'],
                    'mother_email' :  request.json['mother_email'],
                    'mother_phone_number' :  request.json['mother_phone_number']
                }

                db.create_document(data)
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'recuiter/update_position', methods=['POST'])
def update_position():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_position"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                if (request.json['query'] == 0):
                    """update"""
                    doc['positions'][request.json['position']] = {
                        'title': request.json['title'],
                        'type': request.json['type'],
                        'position_type': request.json['position_type'],
                        'description': request.json['description'],
                        'job_other_details': request.json['job_other_details'],
                        'location': request.json['location'],
                        'joining_date': request.json['joining_date'],
                        'ctc': request.json['ctc'],
                        'fixed_gross': request.json['fixed_gross'],
                        'bonus_name': request.json['bonus_name'],
                        'bonus_amount': request.json['bonus_amount'],
                    }

                elif (request.json['query'] == 1):
                    """delete"""
                    doc['positions'][request.json['position']] = -1

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'recuiter/update_schedule', methods=['POST'])
def update_schedule():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_schedule"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_RECUITER,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                if (request.json['query'] == 0):
                    """update"""
                    doc['schedule'][request.json['schedule']] = {
                        'agenda': request.json['agenda'],
                        'date': request.json['date'],
                        'time': request.json['time'],
                        'details': request.json['details'],
                    }

                elif (request.json['query'] == 1):
                    """delete"""
                    doc['schedule'][request.json['schedule']] = -1

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })

@app.route(api_path + 'update_project', methods=['POST'])
def update_project():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_project"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_PROJECTS,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                if (request.json['query'] == 0):
                    """update"""
                    doc['projects'][request.json['project']] = {
                        'title': request.json['project_title'],
                        'project_description': request.json['project_description']
                    }

                elif (request.json['query'] == 1):
                    """delete"""
                    doc['projects'][request.json['project']] = -1

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })


@app.route(api_path + 'add_new_project', methods=['POST'])
def add_new_project():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """add_new_project"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_PROJECTS,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            projectCode = get_random_string(5)
            if (len(result) == 1):
                """doc exists"""
                doc = db[result[0]['_id']]
                doc.fetch()
                project = {
                    'title': request.json['project_title'],
                    'project_description': request.json['project_description']
                }
                doc['projects'][projectCode] = project

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            elif (len(result) == 0):
                """create doc"""
                data = {
                    DB_DOC_TYPE: DB_DOC_STUDENT_PROJECTS,
                    DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                    'projects': {
                        projectCode: {
                            'title' : request.json['project_title'],
                            'project_description' : request.json['project_description']
                        }
                    }
                }

                db.create_document(data)
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully added exprience",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })




@app.route(api_path + 'update_exprience', methods=['POST'])
def update_exprience():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """update_exprience"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_EXPRIENCES,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            if (len(result) == 1):
                doc = db[result[0]['_id']]
                doc.fetch()
                if (request.json['query'] == 0):
                    """update"""
                    doc['expriences'][request.json['exprience']] = {
                        'responsibility': request.json['exprience_responsibility'],
                        'work': request.json['exprience_work'],
                        'company': request.json['exprience_company'],
                    }

                elif (request.json['query'] == 1):
                    """delete"""
                    doc['expriences'][request.json['exprience']] = -1

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })


@app.route(api_path + 'add_new_exprience', methods=['POST'])
def add_new_exprience():
    if 'token' in request.cookies:
        token = request.cookies['token']
        status = verify_token(token)
        if free_from_error(status):
            """add_new_exprience"""
            query = cloudant.query.Query(
                db, selector = {
                                     DB_DOC_TYPE: DB_DOC_STUDENT_EXPRIENCES,
                                     DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                                }
                )
            result = query(limit=100)['docs']
            projectCode = get_random_string(5)
            if (len(result) == 1):
                """doc exists"""
                doc = db[result[0]['_id']]
                doc.fetch()
                project = {
                    'responsibility': request.json['exprience_responsibility'],
                    'work': request.json['exprience_work'],
                    'company': request.json['exprience_company'],
                }
                doc['expriences'][projectCode] = project

                doc.save()
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully updated",
                })
            elif (len(result) == 0):
                """create doc"""
                data = {
                    DB_DOC_TYPE: DB_DOC_STUDENT_EXPRIENCES,
                    DB_DOC_FIELD_ROLL_NO: status[DB_DOC_FIELD_ROLL_NO],
                    'expriences': {
                        projectCode: {
                            'responsibility': request.json['exprience_responsibility'],
                            'work': request.json['exprience_work'],
                            'company': request.json['exprience_company'],
                        }
                    }
                }

                db.create_document(data)
                return jsonify({
                    'success': SUCCESS_CODE_VALID,
                    'message': "Successfully added project",
                })
            else:
                return jsonify({
                    'success': SUCCESS_CODE_IN_VALID,
                    'message': "Please try again",
                })
        else:
            return jsonify({
                'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
                'message': "Please try again",
            })
    return jsonify({
        'success': SUCCESS_CODE_IN_VALID_LOG_OUT,
        'message': "Please try again",
    })



@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
