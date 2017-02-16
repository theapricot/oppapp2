print("importing modules...")
from datetime import datetime, date
import time
print("> Flask")
from flask import Flask,session, flash, url_for, redirect, render_template, abort , g, make_response, stream_with_context, request, Response
print("> Flask-sqlalchemy")
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
print("> Flask-login")
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
print("> Flask-uploads")
from flask_uploads import UploadSet, IMAGES, configure_uploads 
from werkzeug.security import generate_password_hash, check_password_hash
import ast, re, uuid
from gevent import monkey
#import eventlet
#import eventlet.wsgi
from natural import date as ndate
from natural import number, size
from flask_socketio import SocketIO


print("initializing...")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ms.db'
app.config['SECRET_KEY'] = 'thesecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploaded'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
sio = SocketIO(app)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

print("forming databi...")    
# FLASK-SQLALCHEMY MANY-TO-MANY RELATIONSHIP TABLE (USERS <-> OPPS) #
relationship_table = db.Table('relationship_table',
    db.Column('user_id', db.Integer,db.ForeignKey('users.id'), nullable=False),
    db.Column('opps_id',db.Integer,db.ForeignKey('opps.id'),nullable=False),
    db.PrimaryKeyConstraint('user_id', 'opps_id') )
    
preferred_relationship_table = db.Table('preferred_relationship_table',
    db.Column('user_id', db.Integer,db.ForeignKey('users.id'), nullable=False),
    db.Column('opps_id',db.Integer,db.ForeignKey('opps.id'),nullable=False),
    db.PrimaryKeyConstraint('user_id', 'opps_id') )
    
photos_likes_table = db.Table('photos_likes_table',
    db.Column('user_id', db.Integer,db.ForeignKey('users.id'), nullable=False),
    db.Column('photo_id',db.Integer,db.ForeignKey('photos.id'),nullable=False),
    db.PrimaryKeyConstraint('user_id', 'photo_id') )
 
users_tags_table = db.Table('users_tags_table',
    db.Column('user_id', db.Integer,db.ForeignKey('users.id'), nullable=False),
    db.Column('tag_id',db.Integer,db.ForeignKey('tags.id'),nullable=False),
    db.PrimaryKeyConstraint('user_id', 'tag_id') )
    
# USERS CLASS #
class Users(db.Model):
    id = db.Column(db.Integer , primary_key=True) # user's internal id for app
    fname = db.Column('fname', db.String(20)) # first name
    lname = db.Column('lname', db.String(20)) # last name
    password = db.Column('password' , db.String(250)) # definitely not the password
    editor = db.Column('editor', db.Boolean) # whether or not user can edit events
    cansignup = db.Column('cansignup', db.Boolean) # whether or not user can sign up for events
    email = db.Column('email',db.String(50),unique=True , index=True) # user's grove city college email address
    gccid = db.Column('gccid', db.Integer, unique=True) # user's grove city college student id
    settings = db.Column('settings', db.String) # settings, stored as JSON/python dict encoded as string
    year = db.Column('year' , db.Integer) # user graduation year
    phone = db.Column('phone', db.Integer)
    tags = db.relationship('Tags', secondary = users_tags_table, backref = 'users')
    feedback = db.relationship('Feedback', backref = 'user')
    photos = db.relationship('Photos', backref = 'user')
    opps = db.relationship('Opps' , secondary = relationship_table, backref='users') # connects user to his or her opps
    preferredOpps = db.relationship('Opps', secondary = preferred_relationship_table, backref='usersPreferred')
    likes = db.relationship('Photos', secondary = photos_likes_table, backref='likers')
    
    # user methods
    def __init__(self ,password , email, admin):
        # does some initializing when user first registers
        self.set_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()
        self.editor = admin
        self.cansignup = True
        self.fname = ''
        self.lname = ''
        self.phone = 0
        self.settings = "{'bcc':0,'pastevents':{}}"
        
    def formatPhone(self):
        phone = str(self.phone)
        if not phone == '':
            return '('+phone[0:3]+') '+phone[3:6]+'-'+phone[6:10]
        else:
            return ''
    
    def formatYear(self):
        return "'"+str(self.year)[2:4]

    def set_password(self , password):
        self.password = generate_password_hash(password)

    def check_password(self , password):
        return check_password_hash(self.password , password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id).encode("utf-8").decode("utf-8")

    def __repr__(self):
        return '<User %r>' % (self.fname)
    
    def is_editor_old(self):
        # returns true if user can edit events
        return self.editor
        
    def is_editor(self):
        # returns true if user can edit events
        for tag in self.tags:
            if tag.sid == "SCO" or tag.sid == "WAM":
                return True
        return False
        
    def is_webadmin(self):
        # returns true if user can edit events
        for tag in self.tags:
            if tag.sid == "WAM":
                return True
        return False
        
    def get_setting(self, setting):
        # returns a specified user setting
        return ast.literal_eval(self.settings)[setting]
        
    def chg_setting(self, name, val):
        sets = ast.literal_eval(self.settings)
        sets[name] = val
        self.settings = str(sets)
        db.session.commit()
       

# OPPS CLASS #
class Opps(db.Model):
    id = db.Column(db.Integer, primary_key=True) # opp internal id for app
    name = db.Column(db.String) # opp event name
    date = db.Column(db.DateTime) # when opp starts (date and time)
    enddate = db.Column(db.DateTime) # when opp ends (date and time)
    techsneeded = db.Column(db.Integer) # the opposite of the number of techs that aren't needed
    desc = db.Column(db.String) # event location
    info = db.Column(db.String) # event extra information 
    uuid = db.Column(db.String)
    deleted = db.Column(db.Boolean)
    locked = db.Column('locked', db.Boolean) # recurring events, like chapels
    feedback = db.relationship('Feedback', backref = 'event')
    
    def __init__(self, name, desc):
        # more boring initialization stuff
        self.name = name
        self.date = datetime.utcnow()
        self.enddate = datetime.utcnow()
        self.desc = desc
        self.info = ""
        self.techsneeded = 0
        self.uuid = uuid.uuid4().hex
        self.deleted = False
        self.locked = 0
        
    def __repr__(self):
        return '<Event \'{}\'>'.format(self.name)
        
    def get_timeline(self):
        # returns a number based on how now is related to when the event is
        now = datetime.now()
        if now < self.date:
            return 0 # if event is upcoming
        elif now > self.date and now < self.enddate:
            return 1 # if event is in progress
        elif now > self.enddate:
            return 2 # if event is over
    
    def get_timesecs(self):
        delta = self.date - datetime.now()
        return delta.seconds + delta.days*24*3600
    
    def get_natural(self, dort):
        if dort == 'd':
            #return ndate.duration(self.date)
            return ndate.duration(self.date)
        elif dort == 't':
            #return ndate.delta(self.enddate, self.date)[0]
            return ndate.delta(self.date, self.enddate)[0]
    def is_today(self):
        if self.date.date() == date.today():
            return 1
        
    def get_shorttime(self, beginningorend):
        if beginningorend == 0:
            d = self.date
        else:
            d = self.enddate
        if d.strftime('%M') == '00':
            timepre = d.strftime('%I')
        else:
            timepre = d.strftime('%I:%M')
        if d.strftime('%p').upper() == 'AM':
            timesuf = 'A'
        else:
            timesuf = 'P'
        return timepre + timesuf

class Feedback(db.Model):
    def __init__(self, data):
        self.data = data
        
    def __repr__(self):
        return '<Feedback for {} by {}>'.format(self.event, self.user)
        
    id = db.Column(db.Integer, primary_key = True)
    data = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    opp_id = db.Column(db.Integer, db.ForeignKey('opps.id'))
    photos = db.relationship('Photos', backref = 'feedback')
    
class Photos(db.Model):
    def __init__(self, path):
        self.path = path
    id = db.Column(db.Integer, primary_key = True)
    path = db.Column(db.String)
    title = db.Column(db.String)
    comment = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'))
    
# TAGS CLASS
class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(3))
    title = db.Column(db.String)
    fontawesomeicon = db.Column(db.String)
    
class Staff(db.Model):
    def __init__(self, id, fname, lname, email):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.email = email
        
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column('fname', db.String)
    lname = db.Column('lname', db.String)
    email = db.Column('email', db.String)
    title = db.Column('title', db.String)
    fontawesomeicon = db.Column('fontawesomeicon', db.String)

class Meta(db.Model):
    def __init__(self, text):
        self.text = text
        
    id = db.Column(db.Integer, primary_key=True)
    welcome_text = db.Column(db.String)
