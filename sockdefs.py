from funcs import *
from flask_socketio import send, emit



print("defining socks...")

# SOCKETIO DEFINITIONS
@sio.on('connect', namespace='/')
def io_connected():
    ip = request.environ['REMOTE_ADDR']
    if current_user.is_authenticated:
        connected[current_user.gccid] = "{} {}".format(current_user.fname, current_user.lname)
        print("{} {} joined the party from {}!".format(current_user.fname, current_user.lname, ip))
    else:
        print("Somebody tried to join from {}".format(ip))
        return False  # not allowed here
    update_online()
    
@sio.on('disconnect', namespace='/')
def io_disconnected():
    if current_user.is_authenticated:
        print("{} {} left the party!".format(current_user.fname, current_user.lname))
        if current_user.gccid in connected:
            del connected[current_user.gccid]
    else:
        return False
    #print('somebody left the party') 
    update_online()
    
@sio.on('oldPwdType')
def oldPwdType(old):
    if current_user.is_authenticated:
        emit('pwdVerify', current_user.check_password(old))
    else:
        return False
    
@sio.on('lockEvent')
def lockEvent(eventid):
    if current_user.is_editor:
        event = Opps.query.get(int(eventid))
        #print(event.name)
        if event.locked:
            event.locked = False
        else:
            event.locked = True
        db.session.commit()
        #print(event.locked)
        emit('eventLock', {'event':str(event.id), 'locked':event.locked})
    else:
        return False

@sio.on('toggleSignUps')
def toggleSignUps():
    if current_user.is_editor:
        allusers = Users.query.order_by(Users.lname.asc())
        if allcansignup():
            for user in allusers:
                user.cansignup = False
        else:
            for user in allusers:
                user.cansignup = True
        db.session.commit()
        emit('signUpsAvailable', {'available': allcansignup()})
    else:
        return False
    
@sio.on('getSignUps')
def getSignUps():
    if current_user.is_authenticated: 
        emit('signUpsAvailable', {'available': allcansignup()})
    else:
        return False
        
@sio.on('changePhoneNumber')
def changePhoneNumber(phone):
    if current_user.is_authenticated:
        current_user.phone = int(phone)
        db.session.commit()
        emit('phoneNumberChanged', current_user.formatPhone())
    else:
        return False
    
@sio.on('signUp')
def signUp( data):
    if current_user.is_authenticated:
        #print(data['opt'])
        usr = current_user
        #print(usr)
        ev = Opps.query.get(int(data['ev']))
        #print(ev)
        if bool(data['opt']):
            if not ev in usr.preferredOpps:
                usr.preferredOpps.append(ev)
                if ev in usr.opps:
                    usr.opps.remove(ev)
            else:
                usr.preferredOpps.remove(ev)
        else:
            if not ev in usr.opps:
                usr.opps.append(ev)
                if ev in usr.preferredOpps:
                    usr.preferredOpps.remove(ev)
            else:
                usr.opps.remove(ev)
            
        db.session.commit()
        events = db.session.query(Opps).filter(Opps.date > datetime.now()).filter(Opps.locked == False).order_by(asc(Opps.date)).all()
        emit('sendEvents', constructEvData(events))
    else:
        return False
    
@sio.on('getEvents')
def getEvents():
    if current_user.is_authenticated:
        events = db.session.query(Opps).filter(Opps.date > datetime.now()).filter(Opps.locked == False).order_by(asc(Opps.date)).all()
        emit('sendEvents', constructEvData(events))
    else:
        return False

@sio.on('getMyEvents')
def getMyEvents():
    if current_user.is_authenticated:
        myEvents = []
        for event in db.session.query(Opps).filter(Opps.date > datetime.now()).filter(Opps.locked == True).order_by(asc(Opps.date)).all():
            if current_user in event.users + event.usersPreferred:
                myEvents.append(event)
        emit('sendMyEvents', constructEvData(myEvents))
    else:
        return False
        
@sio.on('getPastEvents')
def getPastEvents():
    if current_user.is_authenticated:
        myEvents = db.session.query(Opps).filter(Opps.date < datetime.now()).order_by(desc(Opps.date)).all()
        emit('sendPastEvents', constructEvData(myEvents))
    else:
        return False
        
@sio.on('getFBNeeded')
def getFBNeeded():
    if current_user.is_authenticated:
        data = []
        allMyFeedback = db.session.query(Feedback).filter(Feedback.user == current_user).all()
        feedbackDoneFor = []
        for item in allMyFeedback:
            feedbackDoneFor.append(item.event)
        myPastEvents = []
        for event in db.session.query(Opps).filter(Opps.enddate < datetime.now()).order_by(desc(Opps.date)).all():
            if current_user in event.users + event.usersPreferred:
                myPastEvents.append(event)
        feedbackNeeded = list(set(myPastEvents) - set(feedbackDoneFor))
        for event in feedbackNeeded:
            data.append({
                "name":event.name,
                "id":event.id
            })
        emit('sendFBNeeded', data)
    else:
        return False
       
