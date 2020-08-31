from ProjectCode import db
from datetime import datetime

class Patient(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    ssnid = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(200), nullable=False)
    room_type = db.Column(db.String(200), nullable=False)
    date_of_joining = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return "Patient name: " + self.name