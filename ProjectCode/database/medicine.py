from ProjectCode import db
from datetime import datetime

class Medicine(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    ssnid = db.Column(db.String(50), nullable=False)
    medicine = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date_of_issusing = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return "Medicine name: " + self.medicine