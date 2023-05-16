from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, EmailField, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, user_logged_out, logout_user, current_user


# Create a flask instance
app = Flask(__name__)
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

class Stages(db.Model):
    name = db.Column(db.String(200), nullable=False, primary_key=True)
    
    #Create a String
    def __repr__(self):
        return '{}'.format(self.name)
    
#Create Model
class Admin(db.Model, UserMixin):
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), primary_key=True)
    # password = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))

    # Password Hasing
    @property
    def password(self):
        raise AttributeError("Password is not readable !")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    #Create a String
    def __repr__(self):
        return '<Name %r >' % self.name
    
    # overriding get_id()
    def get_id(self):
        return str(self.email)
    
class Client(db.Model):
    case_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    stage_name = db.Column(db.String, db.ForeignKey('stages.name', ondelete='CASCADE'), nullable=False)
    admin_email = db.Column(db.String, db.ForeignKey('admin.email'))
    adminemails = db.relationship('Admin', backref='client')
    stagess = db.relationship('Stages', backref='client')



############ Flask Login Stuff #############
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(str(user_id))


############## Form Classes ################

def get_stage_query():
    return Stages.query

# Create UserForm Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('password_repeat', message="Passwords Must Match !")])
    password_repeat = PasswordField("Confirm Password", validators=[DataRequired()])
    role = SelectField("Role", choices=['Admin', 'Client'], validators=[DataRequired()])
    # stage = QuerySelectField("Stage", query_factory=get_stage_query, get_label='name', validators=[DataRequired()])
    # stage = QuerySelectField("Stage", query_factory=get_stage_query, get_label='name')
    submit = SubmitField("Submit")

# Create UserForm Class
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


#############################################


# Create a route decorator
@app.route('/')
def index():
    return render_template("index.html")

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            
            # Lookup user by Email Address
            user = Admin.query.filter_by(email=email).first()

            if user:
                if check_password_hash(user.password_hash, password):
                    login_user(user,remember=True)
                    return redirect(url_for('dashboard'))
                else:
                    flash("Wrong Password")
            else:
                flash("User Doesn't Exists")                
        return render_template("login.html", form=form)
    return redirect(url_for('dashboard'))


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
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password.data, "sha256")
            user = Admin(name=form.name.data, 
                        email=form.email.data, 
                        password_hash=hashed_pw,
                        role=form.role.data)
            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully")
        else:
            flash(form.email.data + " already registered !! Please try again")
            name = form.name.data
            
        # Nullify Form for next Inputs
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password.data = ''
        form.password_repeat.data = ''
        form.role.data = ''
        # form.stage.data = ''
    our_users = Admin.query.order_by(Admin.date_added)
    stages = Stages.query.order_by(Stages.name)
    return render_template("add_user.html", form=form, our_users=our_users, stages=stages)


# Update User Details
@app.route('/update/<id>', methods=['GET', 'POST'])
def update_user(id):
    form = UserForm()
    name_to_update = Admin.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        db.session.commit()
        flash("User Updated Successfully ")
        our_users = Admin.query.order_by(Admin.date_added)
        return render_template("add_user.html",form=form, our_users = our_users)
    else:
        return render_template("update_user.html",form=form, name_to_update = name_to_update)
    
# Delete User
@app.route('/delete/<email>', methods=['GET', 'POST'])
def delete_user(email):
    user_to_delete = Admin.query.get_or_404(email)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User Deleted Successfully")
    form = UserForm()
    our_users = Admin.query.order_by(Admin.date_added)
    return render_template("add_user.html",form=form, our_users = our_users)

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