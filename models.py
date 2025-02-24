from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  firstname = db.Column(db.String(80), nullable=False)
  lastname = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  type = db.Column(db.String(50))
  __mapper_args__ = {
      'polymorphic_identity': 'user',
      'polymorphic_on': type
  }

  def __init__(self, firstname, lastname, username, email, password):
    self.username = username
    self.firstname = firstname
    self.lastname = lastname
    self.email = email
    self.set_password(password)

  def set_password(self, password):
    """Create hashed password."""
    self.password = generate_password_hash(password, method='scrypt')

  def check_password(self, password):
    """Check hashed password."""
    return check_password_hash(self.password, password)

  def __repr__(self):
    return f'<User {self.id} {self.username} - {self.email}>'

  def get_json(self):
    return {
        "id": self.id,
        "username": self.username,
        "email": self.email,
        "type": self.type
    }

class Graduate(User):

  __mapper_args__ = {
      'polymorphic_identity': 'graduate',
  }

  def __init__(self, firstname, lastname, username, email, password):
   super().__init__(firstname, lastname, username, email, password)

  def apply_job(self, job, file="dummyfilestring"):
    new_application = Application(job, self, file)
    self.applications.append(new_application)
    return new_application

class Employer(User):
  
  __mapper_args__ = {
      'polymorphic_identity': 'employer',
  }

  def __init__(self, firstname, lastname, username, email, password):
   super().__init__(firstname, lastname, username, email, password)

  def create_job(self, title, description, salary, type="full-time"):
    newjob = Job(title, description, salary, type)
    self.jobs.append(newjob)
    return newjob

  def update_app(self, app, status):
    if app.job.employer == self:
      app.status = status
      db.session.commit()

class Job(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), nullable=False)
  description = db.Column(db.String(120), nullable=False)
  salary = db.Column(db.Integer, nullable=False)
  employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  employer = db.relationship('Employer', backref=db.backref('jobs', lazy=True))
  type = db.Column(db.String(80), nullable=False, default='full-time')

  def __init__(self, title, description, salary, type):
    self.title = title
    self.description = description
    self.salary = salary
    self.type = type

  def get_json(self):
    return {
        "id": self.id,
        "title": self.title,
        "description": self.description,
        "salary": self.salary,
        "type": self.type
    }

class Application(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
  graduate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  status = db.Column(db.String(80), nullable=False, default='pending')
  resume_url = db.Column(db.String(120), nullable=False)
  graduate = db.relationship('Graduate', backref=db.backref('applications', lazy=True))
  job = db.relationship('Job', backref=db.backref('applications', lazy=True))

  def __init__(self, job, graduate, url="https://file.pdf"):
    self.job = job
    self.graduate = graduate
    self.resume_url =  url

  def get_json(self):
    return {
        "id": self.id,
        "job_id": self.job_id,
        "job": self.job.title,
        "graduate_id": self.graduate_id,
        "graduate": self.graduate.username,
        "status": self.status,
        "resume_url": self.resume_url
    }
