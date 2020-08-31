from ProjectCode import app,db
from flask import g,session,render_template,request,redirect
from flask.views import MethodView
from ProjectCode.database.user import users
from flask.helpers import url_for
from flask.json import jsonify
from ProjectCode.database.patient import Patient
from ProjectCode.database.medicine import Medicine
from ProjectCode.database.diagnosis import Diagnosis
import random
import string
from datetime import datetime


@app.route('/home')
def home():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    return render_template('home.html', designation=designation)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']
        user = [x for x in users if x.username == username]
        if (user):
            user = user[0]
        else:
            user = None
        if user and user.password == password:
            session['user_id'] = user.id
            session['user_designation'] = user.designation
            designation = user.designation
            return redirect(url_for('.home'))
        else:
            return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')



class Patient_api(MethodView):

    def get(self, patient_ssnid=None):
        if not g.user:
            return redirect('/login')
        designation = g.user.designation
        message = request.args.get('sub')
        patient_ssnid = request.args.get('patient_ssnid')
        if not request.args.get('patient_ssnid'):
            patients = Patient.query.filter(Patient.status=='Active')
            if patients.count() >= 1:
                return render_template('displaypatients.html', patients=patients, designation=designation)
            else:
                return render_template('displaypatients.html', error="We don't have any acive patient in our database :).", designation=designation)
        else:
            try:
                patient = Patient.query.filter(Patient.ssnid==patient_ssnid,Patient.status=='Active')[0]
            except Exception as e:
                return render_template('searchpatient.html', error="Enter Correct Patient SSNID", designation=designation, message=message)
            if message=='update':
                return render_template('updatepatient.html', patient=patient, designation=designation)
            if message=='display':
                return render_template('displaypatient.html', patient=patient, designation=designation)
            if message=='delete':
                return render_template('displaypatient.html', patient=patient, designation=designation, message=message)
            

    def post(self):
        if not g.user:
            return redirect('/login')
        designation = g.user.designation
        patient_ssnid = request.form['ssnid']
        patient_name = request.form['name']
        patient_age = request.form['age']
        patient_address = request.form['address']
        patient_city = request.form['city']
        patient_state = request.form['state']
        patient_room = request.form['room']
        try:
            patient_from_database = Patient.query.filter(Patient.ssnid==patient_ssnid,Patient.status=='Active')[0]
            if (int(patient_from_database.ssnid) == int(patient_ssnid)):
                return render_template('createpatient.html', error="You already have an account on this ssnid "+ str(patient_ssnid), designation=designation)
        except Exception as e:
            pass
        try:
            int(patient_age)
        except Exception as e:
            return render_template('createpatient.html', error_for_age="The Age should be number", designation=designation)
        if (len(patient_ssnid) != 9):
            return render_template('createpatient.html', error_for_ssnid="The length of the account ID should be of 9 digits.", designation=designation)
        patient_id = ''.join(random.choices(string.digits, k=9))
        new_patient = Patient(id=patient_id, ssnid=patient_ssnid, name=patient_name, age=patient_age, address=patient_address, city=patient_city, state=patient_state, room_type=patient_room, status='Active')
        db.session.add(new_patient)
        db.session.commit()
        return render_template('message.html', message="Account created successfully and Customer SSNID is "+ str(patient_ssnid), designation=designation)

        

Patient_view = Patient_api.as_view("patient_api")
app.add_url_rule('/patient', methods=['POST', 'GET'], view_func=Patient_view)


@app.route('/create_patient')
def create_patient():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if designation=='admission desk executive':
        return render_template('createpatient.html',designation=designation)
    else:
        return render_template('message.html', message="You cannot access this url go back to home page :)")


@app.route('/delete_patient')
def get_patient_for_deletion():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if designation!='admission desk executive':
        return render_template('message.html', message="You cannot access this url go back to home page :)")
    return render_template('searchpatient.html', designation=designation, message='delete')


@app.route('/delete_patient/<string:patient_ssnid>')
def delete_patient(patient_ssnid):
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if designation!='admission desk executive':
        return render_template('message.html', message="You cannot access this url go back to home page :)")
    try:
        patient = Patient.query.filter(Patient.ssnid==patient_ssnid,Patient.status=='Active')[0]
    except Exception as e:
        return render_template('message.html', message="There is no patient with this id "+ str(patient_ssnid))
    db.session.delete(patient)
    db.session.commit()
    return render_template('message.html', message="patient deleted successfully with Patient SSNID is "+ str(patient_ssnid))   




@app.route('/search_patient')
def search_patient():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if designation!='admission desk executive':
        return render_template('message.html', message="You cannot access this url go back to home page :)")
    return render_template('searchpatient.html', designation=designation, message='display')


@app.route('/update_patient')
def update_patient():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if designation!='admission desk executive':
        return render_template('message.html', message="You cannot access this url go back to home page :)")
    return render_template('searchpatient.html', designation=designation, message='update')


@app.route('/update_patient/<string:patient_ssnid>', methods=['POST'])
def update_given_patient(patient_ssnid):
    if request.method == 'POST':
        if not g.user:
            return redirect('/login')
        designation = g.user.designation
        if designation!='admission desk executive':
            return render_template('message.html', message="You cannot access this url go back to home page :)")
        patient = Patient.query.filter_by(ssnid=patient_ssnid)[0]
        try:
            patient_age = request.form['age']
            int(patient_age)
        except Exception as e:
            return render_template('update.html', error="The age should be a number.", patient=patient, designation=designation)
        patient.name = request.form['name']
        patient.age = request.form['age']
        patient.address = request.form['address']
        patient.room_type = request.form['room']
        patient.state = request.form['state']
        patient.city = request.form['city']
        db.session.commit()
        return render_template('message.html', message="patient updated successfully and Customer SSNID is "+ str(patient.ssnid), designation=designation)



@app.route('/medicines_for_patient', methods=['GET', 'POST'])
def medicines_for_patient():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if designation!='pharmacist':
        return render_template('message.html', message="You cannot access this url, go back to home page :)")
    if request.method == 'POST':
        medicine_message = None
        patient_ssnid = request.form['ssnid']
        try:
            patient = Patient.query.filter(Patient.ssnid==patient_ssnid,Patient.status=='Active')[0]
        except Exception as e:
            return render_template('search_patient_with_medicines.html', message="Patient not found with the given SSNID "+patient_ssnid, designation=designation)
        medicines = Medicine.query.filter_by(ssnid=patient_ssnid)
        if medicines.count() == 0:
            medicine_message = "No medicine has issused to patient with the given SSNID "+patient_ssnid
        if medicine_message != None:
            return render_template('patient_with_medicine.html',patient=patient,message=medicine_message, designation=designation)
        else:
            return render_template('patient_with_medicine.html',patient=patient,medicines=medicines, designation=designation)
    else:
        return render_template('search_patient_with_medicines.html',designation=designation)


@app.route('/add_medicine/<string:patient_ssnid>', methods=['POST'])
def add_medicine(patient_ssnid):
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if request.method == 'POST':
        if designation!='pharmacist':
            return render_template('message.html', message="You cannot access this url, go back to home page :)")
        medicine_name = request.form['mname']
        medicine_quantity = request.form['quantity']
        medicine_amount = request.form['amount']
        medicine_id = ''.join(random.choices(string.digits, k=9))
        new_medicine = Medicine(id=medicine_id, ssnid=patient_ssnid, medicine=medicine_name, quantity=medicine_quantity, amount=medicine_amount)
        db.session.add(new_medicine)
        db.session.commit()
        return render_template('message.html', message="Medicine added successfully to customer with Customer SSNID is "+ str(patient_ssnid), designation=designation)
 

@app.route('/diagnosis_for_patient', methods=['GET', 'POST'])
def diagnosis_for_patient():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if designation!='diagnostics executive':
        return render_template('message.html', message="You cannot access this url, go back to home page :)")
    if request.method == 'POST':
        diagnoses_message = None
        patient_ssnid = request.form['ssnid']
        try:
            patient = Patient.query.filter(Patient.ssnid==patient_ssnid,Patient.status=='Active')[0]
        except Exception as e:
            return render_template('search_patient_with_diagnoses.html', message="Patient not found with the given SSNID "+patient_ssnid, designation=designation)
        try:
            diagnoses = Diagnosis.query.filter_by(ssnid=patient_ssnid)
            if diagnoses.count() == 0:
                diagnoses_message = "No diagnosis has given to patient with the given SSNID "+patient_ssnid
        except Exception as e:
            diagnoses_message = "No diagnosis has given to patient with the given SSNID "+patient_ssnid
        if diagnoses_message:
            return render_template('patient_with_diagnoses.html',patient=patient,message=diagnoses_message, designation=designation)
        else:
            return render_template('patient_with_diagnoses.html',patient=patient,diagnoses=diagnoses, designation=designation)
    else:
        return render_template('search_patient_with_diagnoses.html',designation=designation)


@app.route('/add_diagnosis/<string:patient_ssnid>', methods=['POST'])
def add_diagnosis(patient_ssnid):
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if request.method == 'POST':
        if designation!='diagnostics executive':
            return render_template('message.html', message="You cannot access this url, go back to home page :)")
        diagnosis_name = request.form['dname']
        diagnosis_amount = request.form['amount']
        diagnosis_id = ''.join(random.choices(string.digits, k=9))
        new_diagnosis = Diagnosis(id=diagnosis_id, ssnid=patient_ssnid, diagnosis=diagnosis_name, amount=diagnosis_amount)
        db.session.add(new_diagnosis)
        db.session.commit()
        return render_template('message.html', message="Diagnosis added successfully to patient with patient SSNID is "+ str(patient_ssnid), designation=designation)



@app.route('/patients_full_detail', methods=['GET', 'POST'])
def patients_full_detail():
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if request.method == 'POST':
        diagnoses_message = None
        medicine_message = None
        patient_ssnid = request.form['ssnid']
        try:
            patient = Patient.query.filter(Patient.ssnid==patient_ssnid,Patient.status=='Active')[0]
        except Exception as e:
            return render_template('search_patient_complete_details.html', message="Patient not found with the given SSNID "+patient_ssnid)

        try:
            diagnoses = Diagnosis.query.filter_by(ssnid=patient_ssnid)
            if diagnoses.count() == 0:
                diagnoses_message = "No diagnosis has given to patient with the given SSNID "+patient_ssnid
        except Exception as e:
            diagnoses_message = "No diagnosis has given to patient with the given SSNID "+patient_ssnid
        date_of_discharge = datetime.now()
        # doj = patient.date_of_joining
        doj = datetime(2020, 6, 27, 23, 8, 15)
        difference = date_of_discharge - doj
        days  = difference.days
        duration_in_s = difference.total_seconds()                        
        days  = divmod(duration_in_s, 86400)[0] 
        days = int(days)
        if patient.room_type == 'general ward':
            price_for_room = 2000
        elif patient.room_type == 'semi sharing':
            price_for_room = 4000
        elif patient.room_type == 'single room':
            price_for_room = 8000
        totalPriceForRoom = days * price_for_room
        medicines = Medicine.query.filter_by(ssnid=patient_ssnid)
        if medicines.count() == 0:
            medicine_message = "No medicine has issused to patient with the given SSNID "+patient_ssnid
        if medicine_message and diagnoses_message:
            return render_template('discharge.html',patient=patient,medMessage=medicine_message,diaMessage=diagnoses_message, date_of_discharge=date_of_discharge, days=days, totalPriceForRoom=totalPriceForRoom, designation=designation)
        if medicine_message != None:
            return render_template('discharge.html',patient=patient,medMessage=medicine_message,diagnoses=diagnoses, date_of_discharge=date_of_discharge, days=days, totalPriceForRoom=totalPriceForRoom, designation=designation)
        if diagnoses_message:
            return render_template('discharge.html',patient=patient,diaMessage=diagnoses_message,medicines=medicines, date_of_discharge=date_of_discharge, days=days, totalPriceForRoom=totalPriceForRoom, designation=designation)
        else:
            return render_template('discharge.html',patient=patient,diagnoses=diagnoses,medicines=medicines, date_of_discharge=date_of_discharge, days=days, totalPriceForRoom=totalPriceForRoom, designation=designation)
    else:
        return render_template('search_patient_complete_details.html',designation=designation)



@app.route('/discharge/<string:patient_ssnid>', methods=['POST'])
def discharge(patient_ssnid):
    if not g.user:
        return redirect('/login')
    designation = g.user.designation
    if request.method == 'POST':
        patient = Patient.query.filter(Patient.ssnid==patient_ssnid,Patient.status=='Active')[0]
        patient.status = 'Discharge'
        db.session.commit()
        return render_template('message.html', message="Patient with patient SSNID is "+ str(patient_ssnid) + " is discharged.", designation=designation)
        