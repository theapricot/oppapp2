print("importing model...")
from models import *
data = []
#print("loading events...")
events = db.session.query(Opps).filter(Opps.date > datetime.now()).filter(Opps.locked == False).all()
alldates = [-1]
i = 1
j = 0
for event in events:
	alldates.append(event.date.day)
	evdata = {"name":event.name,
			  "date":event.date.strftime("%B %m"),
			  "id":event.id,
			  "time":event.date.strftime("%-I%M") + " - " + event.enddate.strftime("%-I%M %p"),
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
		data.append({"weekday":event.date.strftime("%a"),"date":event.date.strftime("%b %m"),"events":[evdata]})
		j += 1
	i += 1
	#print(j-1)
	#print(i)
print(data)

    #data = [{
	#"weekday": "Su",
	#"date": "Sep 20",
	#"events": [{
		#"name": "AO Glow",
		#"date": "January 26",
		#"time": "8 - 9:25 PM",
		#"id": 23,
		#"info": "Dance lighting/sound equipment",
		#"attendees": ["erik", "john"]
	#}, {
		#"name": "OB Freshman Talent Show Rehearsal",
		#"date": "April 69",
		#"time": "1 - 2 PM",
		#"id": 23,
		#"info": "Audio/lights, various instrument setups *preferably someone who can also work actual event",
		#"attendees": ["steve", "ricky"]
	#}]
    #}]
