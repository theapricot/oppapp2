from models import *
connected = {}

# FUNCTION DEFINITIONS #
def allcansignup(): 
    # returns true if property "cansignup" is true for all users 
    # (used for sign-ups open/closed switch on editor page)
    return all([a[0] for a in Users.query.with_entities(Users.cansignup).all()])

def changesetting(usr, name, val):
    # settings are stored as JSON/python dict encoded as a string in users database table
    # this method allows easy setting of these settings
    sets = ast.literal_eval(usr.settings)
    sets[name] = val
    usr.settings = str(sets)
    db.session.commit()
    
def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    #rv.enable_buffering(5)
    return rv
   
def update_online():
    #print(connected)
    sio.emit('update_online', connected)
    
def constructEvData(events):
    data = []
    #print("loading events...")
    
    alldates = [-1]
    i = 1
    j = 0
    for event in events:
        alldates.append(event.date.day)
        evdata = {"name":event.name,
                  "date":event.date.strftime("%B %d"),
                  "id":event.id,
                  "time":event.date.strftime("%-I:%M%p"),
                  "endtime":event.enddate.strftime("%-I:%M%p"),
                  "info":event.info,
                  "location":event.desc,
                  "mystatus":0,
                  "attendees":[]}
        if current_user in event.users:
            evdata['mystatus'] = 1
        if current_user in event.usersPreferred:
            evdata['mystatus'] = 2
            
        for dude in event.users + event.usersPreferred:
            evdata['attendees'].append(dude.fname + ' ' + dude.lname)
        if event.date.day == alldates[i-1]:
            # append to events
            #print("appended to old!")
            data[j-1]['events'].append(evdata)
        else:
            # make new weekday
            #print("new weekday!")
            data.append({"weekday":event.date.strftime("%a"),"date":event.date.strftime("%b %d"),"events":[evdata]})
            j += 1
        i += 1
    return data
