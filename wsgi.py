import click, sys

from app import app
from sqlalchemy.exc import IntegrityError
from models import db, Graduate, Employer, Application
from controllers import get_job_applications, get_all_applications



@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  db.drop_all()
  db.init_app(app)
  db.create_all()

  bob = Employer(firstname="Bob", lastname="Smith", username="bob", email="plsgq@example.com", password="password")
  john = Graduate(firstname="John",  lastname="Doe", username="john", email="mynbi@example.com", password="password")
  newjob = bob.create_job(title="Software Engineer", description="Software Engineer", salary=10000)
  new_application = john.apply_job(newjob)
  bob.update_app(new_application, "accepted")
  db.session.add_all([bob, john, newjob, new_application])
  db.session.commit()
  print('database intialized')


@app.cli.command("get-apps")
@click.argument("job_id", type=int, default=1)
def get_apps(job_id):
  print(get_job_applications(job_id))


@app.cli.command("get-all-apps")
def get_all_apps():
  print(get_all_applications())