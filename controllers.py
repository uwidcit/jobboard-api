from models import db, User, Graduate, Employer, Job, Application
from flask_jwt_extended import (
  JWTManager, 
  create_access_token,
)

#If username and passwords match return a token if not return None
def login_user(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    return create_access_token(identity=user.id)
  return None

def get_all_applications():
  return Application.query.all()

def create_job(emp_id, title, description, salary, type):
  job = Job(title, description, salary, type)
  db.session.add(job)
  db.session.commit()

def create_application(job_id, graduate_id, url):
  if(Job.query.get(job_id) and Graduate.query.get(graduate_id)):
    app = Application(job_id, graduate_id, url)
    db.session.add(app)
    db.session.commit()
  else:
    return None

def get_my_applications(graduate_id):
  return Application.query.filter_by(graduate_id=graduate_id).all()

def get_job_applications(job_id):
  return Application.query.filter_by(job_id=job_id).all()

def get_all_my_applications(employer_id):
  return Application.query\
      .join(Job)\
      .filter(Job.employer_id == employer_id)\
      .all()

def update_app(app_id, status):
# retrieve the app
# if exists update it to status
  app = Application.query.get(app_id)
  if(app):
    app.status = status
    db.session.commit()
  return app

def update_app2(app_id, status, current_user):
  app = Application.query.get(app_id)
  if(app):
      current_user.update_app(app, status)


def upload_to_service(file):
  # upload to service
  return "https://file.pdf"

def create_app2(job_id, current_user):
  job = Job.query.get(job_id)
  app = None
  if job:
    app = current_user.apply_job(job)
  return app