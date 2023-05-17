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
from datetime import datetime

# Create a flask instance
app = Flask(__name__)
app.config['DEBUG'] = True
app.app_context().push()

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
    id = db.Column(db.String(200), primary_key=True)
    pwd = db.Column(db.String(256), nullable=False)
    
    baseline_survey_completion_status = db.Column(db.String(256))
    baseline_survey_start_date = db.Column(db.Date)
    baseline_survey_completion_date = db.Column(db.Date)
    baseline_survey_wave_number = db.Column(db.Integer)

    followUp_one_survey_start_date = db.Column(db.Date)
    followUp_one_completion_status = db.Column(db.String(256))
    followUp_one_completion_date = db.Column(db.Date)
    followUp_one_wave_number = db.Column(db.Integer)
    
    followUp_two_survey_start_date = db.Column(db.Date)
    followUp_two_completion_status = db.Column(db.String(256))
    followUp_two_completion_date = db.Column(db.String(256))
    followUp_two_wave_number = db.Column(db.Integer)

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

    last_invite_date = db.Column(db.DateTime, default=datetime.utcnow)
    number_of_invites = db.Column(db.Integer, default=0)
    invitation_sent = db.Column(db.Boolean, default=False)

    new_prescription_treatment_start_date = db.Column(db.String(20))

    baseline_survey_completion_status = db.Column(db.String(256))
    baseline_survey_start_date = db.Column(db.Date)
    baseline_survey_completion_date = db.Column(db.Date)
    baseline_survey_wave_number = db.Column(db.Integer)

    followUp_one_survey_start_date = db.Column(db.Date)
    followUp_one_completion_status = db.Column(db.String(256))
    followUp_one_completion_date = db.Column(db.Date)
    followUp_one_wave_number = db.Column(db.Integer)
    
    followUp_two_survey_start_date = db.Column(db.Date)
    followUp_two_completion_status = db.Column(db.String(256))
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

# Create UserForm Class
class PatientForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    date = DateField("Last visit Date", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Login Class
class LoginForm(FlaskForm):
    id = StringField("User ID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


#############################################

## DateFormat Convert Utility
@app.template_filter('datetimeformat')
def datetimeformat(value):
    x = value.split("-")
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
    return render_template("index.html")


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
    my_patients = Patient.query.order_by(Patient.date_added)
    my_ECP = Patient.query.filter_by(id=current_user.id)

    if form.validate_on_submit():
        user = Patient.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Patient(id=generate_patients_id(), name=form.name.data, 
                        email=form.email.data, 
                        last_visit_date=form.date.data,
                        physician_id_ref_link = current_user
                        )
            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully")
            return redirect(url_for('add_patient'))
        else:
            flash(form.email.data + " already registered !! Please try again")
    return render_template("add_patient.html", 
                           form=form, 
                           my_ECP=my_ECP, 
                           my_patients=my_patients, 
                           current_user=current_user
                           )


# # Update User Details
# @app.route('/update/<id>', methods=['GET', 'POST'])
# def update_user(id):
#     form = UserForm()
#     name_to_update = Admin.query.get_or_404(id)
#     if request.method == "POST":
#         name_to_update.name = request.form['name']
#         name_to_update.email = request.form['email']
#         name_to_update.fav_color = request.form['fav_color']
#         db.session.commit()
#         flash("User Updated Successfully ")
#         our_users = Admin.query.order_by(Admin.date_added)
#         return render_template("add_user.html",form=form, our_users = our_users)
#     else:
#         return render_template("update_user.html",form=form, name_to_update = name_to_update)
    
# # Delete User
# @app.route('/delete/<email>', methods=['GET', 'POST'])
# def delete_user(email):
#     user_to_delete = Admin.query.get_or_404(email)
#     db.session.delete(user_to_delete)
#     db.session.commit()
#     flash("User Deleted Successfully")
#     form = UserForm()
#     our_users = Admin.query.order_by(Admin.date_added)
#     return render_template("add_user.html",form=form, our_users = our_users)

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