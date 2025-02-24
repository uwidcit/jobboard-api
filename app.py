from flask import Flask, json, jsonify, request
from functools import wraps
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    get_jwt_identity, 
    set_access_cookies,
    unset_access_cookies,
    jwt_required,
    current_user
)

from models import db, User, Job, Application, Employer, Graduate
from controllers import login_user, upload_to_service

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db.init_app(app)
app.app_context().push()
CORS(app)

jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user_id):
  return user_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

# customn decorator authorize routes for admin or regular user
def login_required(required_class):

    def wrapper(f):

        @wraps(f)
        @jwt_required()  # Ensure JWT authentication
        def decorated_function(*args, **kwargs):
            user = required_class.query.get(get_jwt_identity())
            print(user.__class__, required_class,
                  user.__class__ == required_class)
            if user.__class__ != required_class:  # Check class equality
                return jsonify(message='Invalid user role'), 403
            return f(*args, **kwargs)

        return decorated_function

    return wrapper


@app.route('/')
def index():
    return '<h1>Job Board</h1>'

@app.route('/identify', methods=['GET'])
@jwt_required()
def identify():
    return jsonify(message=f'You are {current_user.get_json()}')

@app.route('/login', methods=['POST'])
def user_login_view():
    data = request.json
    token = login_user(data['username'], data['password'])
    if not token:
        return jsonify(message='bad username or password given'), 403
    response = jsonify(access_token=token)
    set_access_cookies(response, token)
    return response

@app.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    jobs = Job.query.all()
    return jsonify(jobs=[job.get_json() for job in jobs])

@app.route('/jobs', methods=['POST'])
@login_required(Employer)
def create_job():
    data = request.json
    job = current_user.create_job(data['title'], data['description'], data['salary'], data['type'])
    db.session.add(job)
    db.session.commit()
    if job:
        return jsonify(job.get_json())
    return jsonify(message='Job creation failed'), 500


@app.route('/applications', methods=['POST'])
@login_required(Graduate)
def create_application():
    data = request.json
    resume_url = upload_to_service(data['resume'])
    job = Job.query.get(data['job_id'])
    if job:
        app = current_user.apply_job(job, resume_url)
        return jsonify(message=f'Application created {app.get_json()}')
    return jsonify(message='Job not found'), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
