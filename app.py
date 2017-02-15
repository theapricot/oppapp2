mustBeAdmin = ['You must be the webadmin to access this page.','danger']
mustBeStudentCoord = ['You must be a student coordinator to access this page.','danger']
from sockdefs import *
print("forming routes...")

monkey.patch_all()

# MAIN EVENTS PAGE #

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        item = Meta.query.get(1)
        return render_template('index.html', ip = request.environ['REMOTE_ADDR'], item = item)
    
    email = request.form['email'].split('@')[0] + "@gcc.edu"
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = Users.query.filter(Users.email.ilike(email)).first()

    if registered_user is None:
        flash('Username is invalid' , 'danger')
        return redirect(url_for('index'))
    if not registered_user.check_password(password):
        flash('Password is invalid','danger')
        return redirect(url_for('index'))
    login_user(registered_user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not g.user.is_editor():
        flash(mustBeStudentCoord[0],mustBeStudentCoord[1])
        return redirect(url_for('index'))
        
    
    #allusers = Users.query.order_by(Users.lname.asc())
    if request.method == 'POST': # happens when form is submitted (a button is clicked on the page)
            
        def getuserevent(addorremove): 
            # parses string sent by form (add user to/remove user from event)
            # returns the user and opp described by that string
            [userid,eventid] = request.form[addorremove].split(',')
            usr = Users.query.get(int(userid))
            opp = Opps.query.get(int(eventid))
            return [usr, opp]
            
        if 'addtoevent' in request.form: # if "add tech to event" button was clicked
            [usr, opp] = getuserevent('addtoevent')
            usr.opps.append(opp)
        
        if 'lockevent' in request.form:
            opp = Opps.query.get(int(request.form['lockevent']))
            if opp.locked:
                opp.locked = False
            else:
                opp.locked = True
            
        if 'removefromevent' in request.form: # if tech is removed from an event
            [usr, opp] = getuserevent('removefromevent')
            if usr in opp.usersPreferred:
                usr.preferredOpps.remove(opp)
            else:
                usr.opps.remove(opp)
            #flash(usr.fname + ' ' + usr.lname + ' removed from "' + opp.name + '"', 'success')
        
        if 'movetoevent' in request.form: # if tech is moved to different event
            [usrid, frmid, toid] =request.form['movetoevent'].split(',')
            usr = Users.query.get(int(usrid))
            frm = Opps.query.get(int(frmid))
            to = Opps.query.get(int(toid))
            if usr in frm.usersPreferred:
                usr.preferredOpps.remove(frm)
            else:
                usr.opps.remove(frm)
            usr.opps.append(to)
            #flash(usr.fname + ' ' + usr.lname + ' moved from "' + frm.name + '" to "' + to.name + '"', 'success')
            
        if 'togglesignup' in request.form: # if "sign-ups open/closed" button is clicked
            if allcansignup():
                for user in allusers:
                    user.cansignup = False
                #flash('Sign-Ups are now closed.')
            else:
                for user in allusers:
                    user.cansignup = True
                #flash('Sign-Ups are now open.')    
                  
        db.session.commit()
    
    allusers = Users.query.order_by(Users.lname.asc())
    events = Opps.query.filter(Opps.date > datetime.now()).order_by(asc(Opps.date)).all()
    
    def renderAdmin():
        for event in events:
            #time.sleep(.01)
            yield event
    g.user = current_user
    return Response(stream_with_context(stream_template('adminevent.html', eventiter = renderAdmin(), events=events, allusers=allusers)))

@app.route('/past', methods=['GET'])
@login_required
def past():
    # render past events
    if not g.user.is_editor():
        flash(mustBeStudentCoord[0],mustBeStudentCoord[1])
        return redirect(url_for('index'))
    
    allusers = Users.query.order_by(Users.lname.asc())
    events = Opps.query.filter(Opps.date < datetime.now()).order_by(desc(Opps.date)).all()
    
    def render_past():
        for event in events:
            #time.sleep(.01)
            yield event
    g.user = current_user
    return Response(stream_with_context(stream_template('past_event.html', eventiter = render_past(), events=events, allusers=allusers)))
    

@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    allEvents = db.session.query(Opps).filter(Opps.date > datetime.now()).order_by(asc(Opps.date)).all()
    return render_template('events.html',allEvents = allEvents)
            
@app.route('/pastevents', methods=['GET'])
@login_required
def pastevents():
    #allEvents = db.session.query(Opps).filter(Opps.date < datetime.now()).order_by(desc(Opps.date)).all()
    return render_template('pastevents.html')
        

# NEW EVENT PAGE #
@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not g.user.is_editor() and not g.user.is_webadmin():
        flash(mustBeStudentCoord[0],mustBeStudentCoord[1])
        return redirect(url_for('events'))
        
    if request.method == 'POST': # form was submitted
        # do a whole bunch of form verification (is there a better way to do this?)
        if not request.form['title']:
            flash('Title is required', 'danger')
        elif not request.form['location']:
            flash('Location is required', 'danger')
        elif not request.form['time']:
            flash('Start time is requried', 'danger')
        elif not request.form['endtime']:
            flash('End time is required', 'danger')
        elif not request.form['ntechs']:
            flash('Number of techs is required', 'danger')

        else: # finally, if we pass inspection, add the event to the database
            title = request.form['title']
            todo = Opps(title, request.form['location'])
            todo.date = datetime.strptime(request.form['date']+request.form['time'],'%m/%d/%Y%I:%M %p')
            todo.enddate = datetime.strptime(request.form['date']+request.form['endtime'],'%m/%d/%Y%I:%M %p')
            todo.user = g.user
            todo.techsneeded = int(request.form['ntechs'])
            todo.info = request.form['info']
            db.session.add(todo)
            db.session.commit()
            flash('"' + title + '" was successfully created', 'success')
            #flash(todo.uuid,'info')
            return redirect(url_for('admin'))
        
    return render_template('new.html') # page was loaded

    
# EDIT EVENT PAGE #
@app.route('/events/<int:eventID>', methods = ['GET' , 'POST'])
@login_required
def show_or_update(eventID):
    if not g.user.is_editor() and not g.user.is_webadmin():
        flash(mustBeStudentCoord[0],mustBeStudentCoord[1])
        return redirect(url_for('index'))
        
    todo_item = Opps.query.get(eventID)
    if request.method == 'GET':
        return render_template('view.html',todo=todo_item)
    if request.form['submit'] == 'submit':
        todo_item.name = request.form['title']
        todo_item.desc = request.form['location']
        todo_item.date = datetime.strptime(request.form['date']+request.form['time'],'%m/%d/%Y%I:%M %p')
        todo_item.enddate = datetime.strptime(request.form['date']+request.form['endtime'],'%m/%d/%Y%I:%M %p')
        todo_item.techsneeded = request.form['ntechs']
        todo_item.info = request.form['info']
        flash('Event updated.', 'info')
    else:
        db.session.delete(todo_item)
        flash('Event deleted.', 'info')
        
    db.session.commit()
    return redirect(url_for('admin'))
    flash('You are not authorized to edit this todo item','danger')
    return redirect(url_for('show_or_update',todo_id=todo_id))
    
# CLEAR PAST EVENTS METHOD #
@app.route('/clear')
def clear():
    if not g.user.is_editor() and not g.user.is_webadmin():
        flash(mustBeStudentCoord[0],mustBeStudentCoord[1])
        return redirect(url_for('index'))
        
    opps = Opps.query.all()
    for opp in opps:
        if opp.get_timeline() == 2:
            opp.deleted = True
    db.session.commit()
    flash('Cleared Past Events.','info')
    return redirect(url_for('index'))
    
@app.route('/signup')
@login_required
def signup():
    if not g.user.cansignup:
        flash('Sign-ups not available.','danger')
        return redirect(url_for('index'))
    return render_template('signup.html', user = g.user)
    
@app.route('/feedback')
@login_required
def feedback():
    return render_template('feedback.html')
    
@app.route('/feedback/<int:eventID>', methods = ['GET' , 'POST'])
@login_required
def feedbackFor(eventID):
	if request.method == 'GET':
		return render_template('feedbackform.html', event = Opps.query.get(int(eventID)))
	return redirect(url_for('feedback'))
    
@app.route('/upload', methods = ['POST'])
def upload():
	filename = photos.save(request.files['file'])
	print(filename)
	return redirect(url_for('index'))
    
# DOWNLOAD CSV RECEIPT METHOD #
@app.route('/download')
@login_required
def download():
    result = [['Event','Date','Techs']]
    for opp in Opps.query.all():
        item = [opp.name, opp.date]
        for usr in opp.users:
            item.append(usr.fname +' '+ usr.lname)
        result.append(item)

    result = excel.make_response_from_array(result, 'csv', status=200, file_name='opps')
    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=opps.csv"
    return response 
   
@app.route('/mailreceipt')
@login_required
def mailreceipt():
    mailstring = ""
    for opp in Opps.query.all():
        if opp.get_timeline() != 2:
            mailstring += opp.name + " - " + str(opp.date.strftime('%a, %b %-d, %Y')) + "\n"
            for tech in opp.users:
                mailstring += tech.fname + " " + tech.lname + ", "
            mailstring += "\n\n"
    return redirect('mailto:' + g.user.email + '?subject=Work Opps&body=' + mailstring)

# USER PROFILE PAGE #
@app.route('/profile/<gccid>', methods=['GET','POST'])
@login_required
def profile(gccid):
    if request.method == 'POST':
        if 'changepassword' in request.form:
            if g.user.check_password(request.form['oldpwd']):
                if request.form['newpwd1'] == request.form['newpwd2']:
                    g.user.set_password(request.form['newpwd1'])
                    db.session.commit()
                    flash('Password successfully changed.','success')
                else:
                    flash('New passwords do not match.','danger')
            else:
                flash('Old password incorrect','danger')
                
        if 'bcc' in request.form:
            if request.form['bcc'] == "on":
                changesetting(g.user, 'bcc', 1)
            else:
                changesetting(g.user, 'bcc', 0)
    users = Users.query.filter(Users.gccid != gccid).order_by(asc(Users.lname)).all()
    staff = Staff.query.all()
    usr = Users.query.filter(Users.gccid == gccid).first()
    if not usr:
        flash('User '+ gccid +' not found.','danger')
        return redirect(url_for('index'))
    return render_template('profile.html', users = users, usr = usr, staff = staff)

# REGISTER NEW USER PAGE #
@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if not request.form['fname'] or not request.form['lname']:
        flash ('Please enter your name.','danger')
    elif not request.form['email']:
        flash('Please enter an email address.','danger')
    elif not re.match(r"(.*@gcc\.edu)", request.form['email']):
        flash('Please enter a valid GCC email address.','danger')
    elif not re.match(r"(\d{6})", request.form['gccid']):
        flash('Please enter a valid GCC ID number','danger')
    elif request.form['password'] != request.form['password2']:
        flash('Passwords do not match!','danger')
    
    else:
        user = Users(request.form['password'],request.form['email'], 0)
        user.fname = request.form['fname'].title()
        user.lname = request.form['lname'].title()
        user.gccid = int(request.form['gccid'])
        db.session.add(user)
        db.session.commit()
        flash('User successfully registered','success')
        return redirect(url_for('index'))
    return render_template('register.html')
    
    
@app.route('/reset')
def reset():
    pass
@app.route('/reset/<uuid>')
def doreset(uuid):
    pass

# LOGOUT METHOD #
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index')) 

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

# RUN APP #
if __name__ == '__main__':
    print("Starting...")
    sio.run(app, host="0.0.0.0", port=5000)

