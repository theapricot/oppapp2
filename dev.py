print("STARTING WEBSERVER\nImporting models...")
from models import *
print("Starting...")
monkey.patch_all()

# SOCKETIO DEFINITIONS
    
@sio.on('getEvents')
def getEvents(self):
    data = []
    #print("loading events...")
    events = db.session.query(Opps).filter(Opps.date > datetime.now()).filter(Opps.locked == False).all()
    alldates = [-1]
    i = 1
    j = 0
    for event in events:
        alldates.append(event.date.day)
        evdata = {"name":event.name,
                  "date":event.date.strftime("%B %d"),
                  "id":event.id,
                  "time":event.date.strftime("%-I:%M") + " - " + event.enddate.strftime("%-I:%M %p"),
                  "info":event.info,
                  "attendees":[]}
        for dude in event.users:
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

    sio.emit('sendEvents', data)
   
    
@app.route('/')
def index():
    return render_template('signup.html')

# RUN APP #
if __name__ == '__main__':
    socketApp = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 8080)), socketApp)

