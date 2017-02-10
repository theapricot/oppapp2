from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
from datetime import datetime

URL = u'https://webmail.gcc.edu/EWS/Exchange.asmx'
#USERNAME = u'GCC\\azevedoet1'
#PASSWORD = u"qsswew11!"

# Set up the connection to Exchange

def createEvent(username, password, eventName, eventLocation, eventStart, eventEnd, eventBody='', eventAttendees=[]):
	
	username = 'GCC\\' + username
	connection = ExchangeNTLMAuthConnection(url=URL,
	                                        username=username,
	                                        password=password
	                                        )
	
	service = Exchange2010Service(connection)
	
	# Set event properties
	event = service.calendar().new_event(
	  subject = eventName,
	  attendees = eventAttendees,
	  location = eventLocation,
	  start = eventStart,
	  end = eventEnd,
	  html_body = eventBody
	)
	
	# Connect to Exchange and create the event
	event.create()
	
#createEvent('azevedoet1','qsswew11!','Swag Fest','your moms house',datetime.now(),datetime.now(), eventAttendees=['azevedoet1@gcc.edu'])
