#!venv/bin/python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.login import LoginManager
import logging
from twilio.rest import TwilioRestClient

# Creates global Flask app object
# Sets configuration variables from config.py
app = Flask(__name__)
app.config.from_pyfile('../config.py')

# Creates global SQLAlchemy and Migrate objects
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Creates global Manager object and allows migrate.py to work
manager = Manager(app)
manager.add_command('db', MigrateCommand)

lm = LoginManager(app)
lm.login_view = 'home'

#Twilio text client
textClient = TwilioRestClient(app.config["ACCOUNT_SID"], app.config["AUTH_TOKEN"])

from alert import views, models
