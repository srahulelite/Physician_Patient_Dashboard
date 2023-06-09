from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, EmailField, ValidationError, DateField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, user_logged_out, logout_user, current_user
from datetime import datetime, date, timedelta
import schedule
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Create a flask instance
app = Flask(__name__)
app.app_context().push()
app.config['DEBUG'] = True

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ClientAdmin.db'

# Secret Key
app.config['SECRET_KEY'] = "slakfj9*&^&*%98"

# Initialize Database
db = SQLAlchemy(app)

# Migration Configuration
migrate = Migrate(app, db)


############### DATABASE THINGS ##################
   
# Create Physician Model

class Physician(db.Model, UserMixin):
    id = db.Column(db.String(10), primary_key=True)
    pwd = db.Column(db.String(20), nullable=False)

    new_prescription_treatment_start_date = db.Column(db.String(20))
    
    baseline_survey_due_date = db.Column(db.Date,default=datetime.utcnow)
    baseline_survey_start_date = db.Column(db.Date)
    baseline_survey_completion_status = db.Column(db.String(100), default="Available, Not Yet Started")
    baseline_survey_completion_date = db.Column(db.Date)
    baseline_survey_wave_number = db.Column(db.Integer)
    baseline_survey_patient_id = db.Column(db.String(10))

    followUp_one_survey_due_date = db.Column(db.Date)
    followUp_one_survey_start_date = db.Column(db.Date)
    followUp_one_completion_status = db.Column(db.String(100))
    followUp_one_completion_date = db.Column(db.Date)
    followUp_one_wave_number = db.Column(db.Integer)
    followUp_one_patient_id = db.Column(db.String(10))
    
    followUp_two_survey_due_date = db.Column(db.Date)
    followUp_two_survey_start_date = db.Column(db.Date)
    followUp_two_completion_status = db.Column(db.String(100))
    followUp_two_completion_date = db.Column(db.Date)
    followUp_two_wave_number = db.Column(db.Integer)
    followUp_two_patient_id = db.Column(db.String(10))

# Create Patient Model
class Patient(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    last_visit_date = db.Column(db.String(200))
    physician_id = db.Column(db.String, db.ForeignKey('physician.id', ondelete='CASCADE'), nullable=False)
    physician_id_ref_link = db.relationship('Physician', backref='patient')
    active_inactive = db.Column(db.Boolean, default=True)

    last_invite_date = db.Column(db.Date, default=datetime.utcnow)
    number_of_invites = db.Column(db.Integer, default=0)
    invitation_sent = db.Column(db.Boolean, default=False)

    baseline_survey_due_date = db.Column(db.Date)
    baseline_survey_start_date = db.Column(db.Date)
    baseline_survey_completion_status = db.Column(db.String(100))
    baseline_survey_completion_date = db.Column(db.Date)
    baseline_survey_wave_number = db.Column(db.Integer)

    followUp_one_survey_due_date = db.Column(db.Date)
    followUp_one_survey_start_date = db.Column(db.Date)
    followUp_one_completion_status = db.Column(db.String(100))
    followUp_one_completion_date = db.Column(db.Date)
    followUp_one_wave_number = db.Column(db.Integer)
    
    followUp_two_survey_due_date = db.Column(db.Date)
    followUp_two_survey_start_date = db.Column(db.Date)
    followUp_two_completion_status = db.Column(db.String(100))
    followUp_two_completion_date = db.Column(db.Date)
    followUp_two_wave_number = db.Column(db.Integer)

# Create Activity Log Model
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    log_content = db.Column(db.String(120), nullable=False)
    log_date_time = db.Column(db.DateTime, nullable=False)
    system_version = db.Column(db.Integer, default=1)
    source = db.Column(db.String(20), nullable=False)

############ Flask Login Stuff #############
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Physician.query.get(user_id)


############## Form Classes ################

# Create Patient Form Class
class PatientForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3,max=35,message="Name should be in between 3 to 35 characters")])
    email = EmailField("Email", validators=[DataRequired(), Length(min=3,max=35,message="email should be in between 3 to 35 characters")])
    date = DateField("Last visit Date", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_date(form, field):
        if field.data > date.today():
            flash("Last Visit Date could not be after today")
            raise ValidationError("Last Date could not be after today")
        elif field.data < (date.today() - timedelta(days=1)):
            flash("Last Visit Date should not be prior to yesterday")
            raise ValidationError("Last Visit Date should not be prior to yesterday")
        else:
            pass

# Create Login Class
class LoginForm(FlaskForm):
    id = StringField("User ID", validators=[DataRequired(),Length(min=4,max=8,message="ID should be in between 4 to 8 characters")])
    password = PasswordField("Password", validators=[DataRequired(),Length(min=4,max=10,message="Password should be in between 4 to 10 characters")])
    submit = SubmitField("Submit")


#############################################

## DateFormat Convert Utility
@app.template_filter('datetimeformat')
def datetimeformat(value):
    x = value.split("-")
    x = str(x[1]) + "-" + str(x[2]) + "-" + str(x[0])
    value = datetime.strptime(x, "%m-%d-%Y")
    return value.strftime('%m-%d-%Y')

@app.template_filter('dbdatetimeformat')
def dbdatetimeformat(value):
    x = value.strftime('%Y-%m-%d')
    x = x.split("-")
    x = str(x[1]) + "-" + str(x[2]) + "-" + str(x[0])
    value = datetime.strptime(x, "%m-%d-%Y")
    return value.strftime('%m-%d-%Y')

# Index
@app.route('/')
def index():
    # return render_template("index.html")
    return redirect(url_for('login'))

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            id = form.id.data
            password = form.password.data
            
            # Lookup Physician with ID
            user = Physician.query.filter_by(id=id).first()
            
            if user:
                if user.pwd == password:
                    login_user(user,remember=True)
                    return redirect(url_for('add_patient'))
                else:
                    flash("Wrong Password")
            else:
                flash("User Doesn't Exists")                
        return render_template("login.html", form=form)
    return redirect(url_for('add_patient'))


# Dasbhoard page
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")


# Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    current_user = None
    logout_user()
    flash("You have been logged out ")
    return redirect(url_for('login'))

# Add User

def generate_patients_id():
    #PT10001 - #PT99999
    user = Patient.query.order_by(Patient.id.desc()).first()
    if user:
        pt_id_serial = int(user.id[2:])
        new_pt_id = 'PT' + str(pt_id_serial + 1)
    else:
        new_pt_id = 'PT10001'
    return new_pt_id

@app.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    form = PatientForm()
    my_patients = Patient.query.filter_by(physician_id=current_user.id).order_by(Patient.active_inactive.desc(), Patient.id)
    my_ECP = Physician.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():
        user = Patient.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Patient(id=generate_patients_id(), name=form.name.data, 
                        email=form.email.data, 
                        last_visit_date=form.date.data,
                        baseline_survey_due_date = form.date.data,
                        baseline_survey_completion_status = 'Available, Not Yet Started',
                        physician_id_ref_link = current_user
                        )
            db.session.add(user)
            db.session.commit()
            flash("Patient Added Successfully")
            return redirect(url_for('add_patient'))
        else:
            flash(form.email.data + " already registered !! Please try again")
    return render_template("add_patient.html", 
                        form=form, 
                        my_ECP=my_ECP, 
                        my_patients=my_patients, 
                        current_user=current_user
                        )


# Update User Details
@app.route('/update/<id>', methods=['GET', 'POST'])
def update_user(id):
    form = PatientForm()
    my_patients = Patient.query.order_by(Patient.active_inactive.desc(), Patient.id)
    my_ECP = Physician.query.filter_by(id=current_user.id).first()
    patient_to_update = Patient.query.get_or_404(id)
    if form.validate_on_submit():
        if request.method == "POST":
            if((patient_to_update.email == request.form['email']) and (patient_to_update.name == request.form['name']) and (patient_to_update.last_visit_date == request.form['date'])):
                flash("No change entered !")
                return redirect(url_for('add_patient'))
            else:
                #Checking if Last Visit Date Changed
                if (patient_to_update.last_visit_date == request.form['date']):
                    patient_to_update.last_visit_date = request.form['date']
                else:
                    if(ecp_last_wave_completed(current_user.id)):
                        patient_to_update.last_visit_date = request.form['date']
                    else:
                        return redirect(url_for('add_patient'))

                #checking if patient email ID is same as entered in form
                if(patient_to_update.email == request.form['email']):
                    patient_to_update.name = request.form['name']
                    patient_to_update.email = request.form['email']
                    
                    db.session.commit()
                    flash("User Updated Successfully ")
                    return redirect(url_for('add_patient'))
                else:
                    #checking Duplicate email as when update
                    patient_to_update_email_dup_chk = Patient.query.filter_by(email=request.form['email']).first()
                    if patient_to_update_email_dup_chk is None:
                        patient_to_update.name = request.form['name']
                        patient_to_update.email = request.form['email']
                        db.session.commit()
                        flash("Note: You have changed email address")
                        flash("User Updated Successfully ")
                        return redirect(url_for('add_patient'))
                    else:
                        flash("Entered email address to change is already registered with us. Please try with another one !")
                        return render_template("update_patient.html",form=form, patient_to_update=patient_to_update, my_ECP=my_ECP)
        else:
            return render_template("update_patient.html",form=form, patient_to_update=patient_to_update, my_ECP=my_ECP)
    else:
        return render_template("update_patient.html",form=form, patient_to_update=patient_to_update, my_ECP=my_ECP)
    
def ecp_last_wave_completed(id):
    if current_user.followUp_two_completion_status == 'complete':
        last_wave = 2
    elif current_user.followUp_one_completion_status == 'complete':
        last_wave = 1
    elif current_user.baseline_survey_completion_status == 'complete':
        last_wave = 0
    else:
        flash("ECP has not completed the survey")
        last_wave = None
    return last_wave

# Delete User
@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete_user(id):
    my_ECP = Physician.query.filter_by(id=current_user.id).first()
    patient_to_delete = Patient.query.get_or_404(id)
    patient_to_delete.active_inactive = False
    #db.session.delete(patient_to_delete)
    db.session.commit()
    flash("Patient Deleted Successfully")
    # form = PatientForm()
    my_patients = Patient.query.order_by(Patient.active_inactive.desc(), Patient.id)
    return redirect(url_for('add_patient'))

# Send Email
@app.route('/send_email/<id>', methods=['GET', 'POST'])
def send_email(id):
    form = PatientForm()
    # my_patients = Patient.query.order_by(Patient.active_inactive.desc(), Patient.id)
    # if ecp_last_wave_completed(current_user.id):
    patient_to_invite_sent = Patient.query.get_or_404(id)

    url_string = "http://localhost:5000/interncollect?patid=" + patient_to_invite_sent.id + "&phyid=" + current_user.id + "&wave=0&stw=pat"
    
    patient_email_to_invite_sent = patient_to_invite_sent.email
    patient_name = patient_to_invite_sent.name
    msgFrom = 'no-reply@acuitykpcustomsolution.com'
    msgSubject = 'ATLAS Patient Survey Notification'
    msg = MIMEMultipart ()
    msg ['From'] = msgFrom
    msg ['To'] = patient_email_to_invite_sent
    msg ['Subject'] = msgSubject
    message = '<h2>Hi ' + patient_name + ', <br> Hope you are doing well. \
                Please find the link below to fill survey asap.\
                <a href= '+url_string +'> <button>Launch Survey</button></a>'
    try:
        msg.attach (MIMEText (message))
        mailserver = smtplib. SMTP ('email-smtp.eu-west-1.amazonaws.com', 587)
        #identify ourselves to smtp gmail client
        mailserver.ehlo ()
        #secure our email with tls encryption
        mailserver.starttls ()
        #re-identify ourselves as an encrypted connection
        mailserver.ehlo ()
        mailserver.login('AKIAZJB4DCASUVVKDUOJ', 'BC0JtUuOkNq42GGpB6f3aLB8YKuittWah41g7R5Mu3o/')
        mailserver.sendmail (msgFrom, patient_email_to_invite_sent, msg.as_string())
        mailserver.quit ()
        flash("Invitation sent to " + str(patient_email_to_invite_sent))
    except:
        flash("Email may not be sent due to some technical Error")

    patient_to_invite_sent.last_invite_date = datetime.utcnow().date()
    patient_to_invite_sent.number_of_invites = patient_to_invite_sent.number_of_invites + 1
    patient_to_invite_sent.invitation_sent = True
    db.session.commit()
    return redirect(url_for('add_patient'))



############# Collect Data from URL's #########
# http://localhost:5000/collect?Phyid=PHY0101&Patid=PT10001&status=co&ntm=0&stw=ecp&wave=0
# http://localhost:5000/collect?Phyid=PHY0101&Patid=PT10001&status=co&ntm=0&stw=pat&wave=0
#Phyid
#Patid
#status - co, oq, term
#ntm - 0, YYYY-MM
#stw - ecp, pat
#wave - 0-7

@app.route('/interncollect', methods=['GET', 'POST'])
def interncollect():
    response = request.args.to_dict()
    my_ECP = Physician.query.filter_by(id=response['phyid']).first()
    my_PAT = Patient.query.filter_by(id=response['patid']).first()
    if (response['wave'] == '0'):
        # Baseline Data Punching #
        if(response['stw'] == 'ecp'):
            my_ECP.baseline_survey_start_date = date.today()
            my_ECP.baseline_survey_completion_status = "Started, Not Completed"
            db.session.commit()
            url_string = "https://emea.focusvision.com/survey/selfserve/581/230446?list=1&patid=" + my_PAT.id + "&phyid="+ current_user.id
        elif(response['stw'] == 'pat'):
            my_PAT.baseline_survey_start_date = date.today()
            my_PAT.baseline_survey_completion_status = "Started, Not Completed"
            db.session.commit()
            url_string = "https://emea.focusvision.com/survey/selfserve/581/230332?list=1&patid=" + my_PAT.id + "&phyid="+ current_user.id
        else:
            return "Url ReWritten, Please contact support"
        
    
    elif (response['wave'] == '1'):
        # FollowUP 1 Survey Data Punching #
        if(response['stw'] == 'ecp'):
            my_ECP.followUp_one_survey_start_date = date.today()
            my_ECP.followUp_one_completion_status = "Started, Not Completed"
            db.session.commit()
            url_string = "https://emea.focusvision.com/survey/selfserve/581/230503?list=1&ntm=" + my_ECP.new_prescription_treatment_start_date +"&patid=" + my_PAT.id + "&phyid="+ current_user.id
        elif(response['stw'] == 'pat'):
            my_PAT.baseline_survey_start_date = date.today()
            my_PAT.baseline_survey_completion_status = "Started, Not Completed"
            db.session.commit()
            url_string = "https://emea.focusvision.com/survey/selfserve/581/230501?list=1&ntm=" + my_ECP.new_prescription_treatment_start_date +"&patid=" + my_PAT.id + "&phyid="+ current_user.id
        else:
            return "Url ReWritten, Please contact support"
        

    # elif (response['wave'] == '2'):
    #     # FollowUP 1 Data Punching #
    #     if(response['stw'] == 'ecp'):
    #         my_ECP.baseline_survey_start_date = date.today()
    #         my_ECP.baseline_survey_completion_status = "Started, Not Completed"
    #     elif(response['stw'] == 'pat'):
    #         my_PAT.baseline_survey_start_date = date.today()
    #         my_PAT.baseline_survey_completion_status = "Started, Not Completed"
    #     else:
    #         return "Url ReWritten, Please contact support"
    #     url_string = "https://emea.focusvision.com/survey/selfserve/581/230446?interncollect=1&patid=" + my_PAT.id + "&phyid="+ current_user.id

    return redirect(url_string)

@app.route('/collect', methods=['GET', 'POST'])
def collect():
    response = request.args.to_dict()
    my_ECP = Physician.query.filter_by(id=response['Phyid']).first()
    my_PAT = Patient.query.filter_by(id=response['Patid']).first()

    if (response['wave'] == '0'):
        # Baseline Data Punching #
        if(response['stw'] == 'ecp'):
            # Hint: Comparision of ID's is case sensitive

            # print(response['Phyid'])
            if my_ECP:
                if (my_PAT.physician_id ==  my_ECP.id):
                    my_ECP.baseline_survey_completion_status = getStatusOverwritten(response['status'])
                    my_ECP.baseline_survey_completion_date = date.today()
                    my_ECP.baseline_survey_wave_number = int(response['wave'])
                    my_ECP.baseline_survey_patient_id =response['Patid']
                    db.session.commit()

                    ## Success Page
                    return render_template("return_info.html",return_info=getResponsePage(response['status']))
                else:
                    return 'This patient has not been registered with you'
            else:
                return 'This ECP has not been registered.'
        elif (response['stw'] == 'pat'):
            my_patient = Patient.query.filter_by(id=response['Patid']).first()
            try:
                if my_patient:
                    my_patient.baseline_survey_completion_status = getStatusOverwritten(response['status'])
                    my_patient.baseline_survey_completion_date = date.today()
                    my_patient.baseline_survey_wave_number = int(response['wave'])
                    my_patient.physician_id = response['Phyid']
                    my_patient.last_invite_date = datetime.utcnow().date()
                    my_patient.number_of_invites = 0
                    my_patient.invitation_sent = False
                    db.session.commit()
                    ## Success Page
                    return render_template("return_info.html",return_info=getResponsePage(response['status']))
                
                else:
                    return "Patient does not exist !"
            except:
                print("Something went wrong with Patient ID, Please connect with you Support")
        else:
            return 'URL has been rewritten, No response. Please take full screenshot and forward to your Support Team'
    elif(response['wave_number'] == '1'):
        # Do something for wave 1
        return 'something'
    else:
        # Do something for last wave
        return 'something'

# Rephrasing Status
def getStatusOverwritten(status):
    if status == 'co':
        return 'complete'
    elif status == 'oq':
        return 'OverQuota'
    elif status == 'term':
        return "Didn't qualify"

def getResponsePage(status):
    if status == 'co':
        return_info = "Thank you for completing this survey, You will soon receive login information\
         for a dashboard where you can enter eligible patients for the survey and track \
         survey completion. You will be expected to schedule visits with each patient to \
        complete the patient chart portion of the study at each study time point."
    elif status == 'term':
        return_info = "Unfortunately, you have not qualified for this study. Please reach out to \
        <a href='mailto:aathavale@trinitylifesciences.com'>aathavale@trinitylifesciences.com </a> \
         if you have any questions"
    elif status == 'oq':
        return_info = "Unfortunately, you have not qualified for this study. Please reach out to \
        <a href='mailto:aathavale@trinitylifesciences.com'>aathavale@trinitylifesciences.com </a> \
        if you have any questions"
    else:
        return_info = "Wrong return Code !! Please contact your Support Team" 
    return return_info
    
###### Cron Jobs #######
# def job():
#     print("I'm working...")

# # schedule.every(5).seconds.do(job)

# # schedule.every(8).hours.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)


############## Errors ###############
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

############## Errors ###############

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
