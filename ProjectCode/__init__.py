from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config.from_object(Config)


db = SQLAlchemy(app)

from ProjectCode import routes
from ProjectCode.database.patient import Patient
from ProjectCode.database.medicine import Medicine
from ProjectCode.database.diagnosis import Diagnosis