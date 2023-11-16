from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import AvailableSectionsForNewLine, ChosenSectionsForNewLine, User
from app.forms import EditProfileForm
from app.forms import EmptyForm
from app.forms import newStationAdminForm
from app.models import Station
from app.forms import EditStationForm
from flask import render_template, url_for, flash, redirect
from app.forms import SectionForm
from app.models import Section
from app.forms import SectionForm
from app.forms import EventForm
from app.models import Event
from datetime import datetime
from flask import request, render_template, flash, redirect, url_for, session
from app import app, db
from app.models import Line, Section, line_sections
from app.models import User, Role
from flask_security.decorators import roles_required
from app.forms import EditUserForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, join


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))




@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    form = EmptyForm()
    return render_template('user.html', user=user, form=form)    
    
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        db.session.commit() 


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile', form=form) 

        

@app.route('/newStationAdmin', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def newStationAdmin():
    form = newStationAdminForm()
    if form.validate_on_submit():
        station = Station(nameOfStation=form.nameOfStation.data, address=form.address.data, coordinates=form.coordinates.data)
        db.session.add(station)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('newStationAdmin.html', form=form)

@app.route('/editStationsAdmin')
@roles_required('admin')
def editStationsAdmin():
    stations = Station.query.all()
    return render_template('editStationsAdmin.html', stations=stations)



from sqlalchemy.exc import IntegrityError

@app.route('/deleteStation/<int:id>', methods=['POST'])
@roles_required('admin')
def deleteStation(id):
    stationToDelete = Station.query.get_or_404(id)
    
    try:
        db.session.delete(stationToDelete)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Bahnhof ist in Verwendung und kann nicht gelöscht werden.')
        return redirect(url_for('editStationsAdmin'))

    return redirect(url_for('editStationsAdmin'))


@app.route('/editSingleStation/<int:id>', methods=['GET', 'POST'])
@roles_required('admin')
def editSingleStation(id):
    station = Station.query.get_or_404(id)
    form = EditStationForm()

    if form.validate_on_submit():
        station.nameOfStation = form.nameOfStation.data
        station.address = form.address.data
        station.coordinates = form.coordinates.data
        db.session.commit()
        flash('Die Änderungen wurden erfolgreich durchgeführt.')
        return redirect(url_for('editSingleStation', id=station.id))

    elif request.method == 'GET':
        form.nameOfStation.data = station.nameOfStation
        form.address.data = station.address
        form.coordinates.data = station.coordinates

    return render_template('editSingleStation.html', title='Edit Station', form=form)




@app.route('/newSectionAdmin', methods=['GET', 'POST'])
@roles_required('admin')
def newSectionAdmin():
    form = SectionForm()
    form.startStation.choices = [(s.id, s.nameOfStation) for s in Station.query.all()]
    form.endStation.choices = [(s.id, s.nameOfStation) for s in Station.query.all()]
    if form.validate_on_submit():
        section = Section(startStation=form.startStation.data, endStation=form.endStation.data, fee=form.fee.data, distance=form.distance.data, maxSpeed=form.maxSpeed.data, trackWidth=form.trackWidth.data)
        db.session.add(section)
        db.session.commit()
        flash('Neuer Abschnitt wurde erstellt.', 'success')
        return redirect(url_for('index'))
    return render_template('newSectionAdmin.html', title='Neuer Abschnitt', form=form)

@app.route('/editSectionsAdmin')
@roles_required('admin')
def editSectionsAdmin():
    sections = Section.query.all()
    return render_template('editSectionsAdmin.html', sections=sections)


from sqlalchemy.exc import IntegrityError

@app.route('/deleteSection/<int:id>', methods=['POST'])
@roles_required('admin')
def deleteSection(id):
    sectionToDelete = Section.query.get_or_404(id)

    try:
        db.session.delete(sectionToDelete)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Abschnitt ist noch in Verwendung und kann nicht gelöscht werden.', 'error')
        return redirect(url_for('editSectionsAdmin'))

    return redirect(url_for('editSectionsAdmin'))




@app.route('/editSingleSection/<int:id>', methods=['GET', 'POST'])
@roles_required('admin')
def editSingleSection(id):
    section = Section.query.get_or_404(id)
    form = SectionForm()

    # Check if the section is part of a line or multiple lines
    is_part_of_line = Line.query.filter(Line.sections.contains(section)).first() is not None

    form.startStation.choices = [(s.id, s.nameOfStation) for s in Station.query.all()]
    form.endStation.choices = [(s.id, s.nameOfStation) for s in Station.query.all()]

    # If the section is part of a line, disable the startStation, endStation, and trackWidth fields
    if is_part_of_line:
        form.startStation.render_kw = {'disabled': 'disabled'}
        form.endStation.render_kw = {'disabled': 'disabled'}
        form.trackWidth.render_kw = {'disabled': 'disabled'}

    if form.validate_on_submit():
        section.startStation = form.startStation.data
        section.endStation = form.endStation.data
        section.fee = form.fee.data
        section.distance = form.distance.data
        section.maxSpeed = form.maxSpeed.data
        section.trackWidth = form.trackWidth.data
        db.session.commit()
        flash('Die Änderungen wurden erfolgreich durchgeführt.')
        return redirect(url_for('editSingleSection', id=section.id))

    elif request.method == 'GET':
        form.startStation.data = section.startStation
        form.endStation.data = section.endStation
        form.fee.data = section.fee
        form.distance.data = section.distance
        form.maxSpeed.data = section.maxSpeed
        form.trackWidth.data = section.trackWidth

    return render_template('editSingleSection.html', title='Edit Section', form=form)



@app.route('/newEventAdmin', methods=['GET', 'POST'])
@roles_required('admin')
def newEventAdmin():
    form = EventForm()
    form.section.choices = [(s.id, s.sectionName) for s in Section.query.order_by(Section.id).all()]
    if form.validate_on_submit():
        event = Event(section=form.section.data, officialText=form.officialText.data, internalText=form.internalText.data)
        if form.endDate.data:
            event.endDate = datetime.strptime(form.endDate.data, '%Y-%m-%d')
        db.session.add(event)
        db.session.commit()
        flash('Das Ereignis wurde erfolgreich hinzugefügt.')
        return redirect(url_for('index'))
    return render_template('newEventAdmin.html', title='Add Event', form=form)



@app.route('/editEventsAdmin')
@roles_required('admin')
def editEventsAdmin():
    events = Event.query.all()
    return render_template('editEventsAdmin.html', events=events)


@app.route('/editSingleEvent/<int:id>', methods=['GET', 'POST'])
@roles_required('admin')
def editSingleEvent(id):
    event = Event.query.get_or_404(id)
    form = EventForm()
    form.section.choices = [(s.id, s.sectionName) for s in Section.query.order_by(Section.id).all()]
    if form.validate_on_submit():
        event.section = form.section.data
        event.officialText = form.officialText.data
        event.internalText = form.internalText.data
        if form.endDate.data:
            try:
                event.endDate = datetime.strptime(form.endDate.data, '%Y-%m-%d')
            except ValueError:
                event.endDate = None
        db.session.commit()
        flash('Die Änderungen wurden erfolgreich durchgeführt.')
        return redirect(url_for('editSingleEvent', id=event.id))
    elif request.method == 'GET':
        form.section.data = event.section
        form.officialText.data = event.officialText
        form.internalText.data = event.internalText
        form.endDate.data = event.endDate.strftime('%Y-%m-%d') if event.endDate else ''
    return render_template('editSingleEvent.html', title='Edit Event', form=form)



@app.route('/deleteEvent/<int:id>', methods=['POST'])
@roles_required('admin')
def deleteEvent(id):
    eventToDelete = Event.query.get_or_404(id)
    try:
        db.session.delete(eventToDelete)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Das Ereignis kann nicht gelöscht werden, da es von anderen Datensätzen referenziert wird.')
    else:
        flash('Das Ereignis wurde gelöscht.')
    return redirect(url_for('editEventsAdmin'))



@app.route('/newLineAdminStart')
@roles_required('admin')
def newLineAdminStart():
    return render_template('newLineAdminStart.html')

@app.route('/newLineAdminSectionsAssistantPrepareDB', methods=['POST'])
@roles_required('admin')
def newLineAdminSectionsAssistantPrepareDB():
    # Clear the chosen_sections_for_new_line table
    ChosenSectionsForNewLine.query.delete()

    # Clear the available_sections_for_new_line table
    AvailableSectionsForNewLine.query.delete()

    # Get all existing sections
    all_sections = Section.query.all()

    # Add references to all sections in the available_sections_for_new_line table
    for section in all_sections:
        new_available_section = AvailableSectionsForNewLine(section_id=section.id)
        db.session.add(new_available_section)

    db.session.commit()

    return redirect(url_for('newLineAdminSectionsAssistantFrontend'))


@app.route('/newLineAdminSectionsAssistantFrontend')
@roles_required('admin')
def newLineAdminSectionsAssistantFrontend():
    chosen_sections = ChosenSectionsForNewLine.query.all()
    available_sections = AvailableSectionsForNewLine.query.all()

    return render_template('newLineAdminSectionsAssistantFrontend.html', chosen_sections=chosen_sections, available_sections=available_sections)

from flask import request

@app.route('/moveSectionToChosen/<int:section_id>', methods=['POST'])
@roles_required('admin')
def moveSectionToChosen(section_id):
    # Get the section from the Section table
    section = Section.query.get(section_id)

    # Add this section to the ChosenSectionsForNewLine table
    chosen_sections = ChosenSectionsForNewLine.query.all()
    order = 0 if not chosen_sections else chosen_sections[-1].order + 1
    chosen_section = ChosenSectionsForNewLine(section_id=section.id, order=order)
    db.session.add(chosen_section)
    db.session.commit()

    # Get the last section from the ChosenSectionsForNewLine table
    last_section = ChosenSectionsForNewLine.query.order_by(ChosenSectionsForNewLine.order.desc()).first()

    # Get all sections from the Section table where the startStation equals the endStation of the last section
    available_sections = Section.query.filter_by(startStation=last_section.section_rel.endStation).all()
    
    # Clear the AvailableSectionsForNewLine table
    AvailableSectionsForNewLine.query.delete()

    # Add the sections from step 4 to the AvailableSectionsForNewLine table
    for section in available_sections:
        available_section = AvailableSectionsForNewLine(section_id=section.id)
        db.session.add(available_section)

    # Commit the changes to the database
    db.session.commit()

    #This is necessary because the route can be accessed from multiple other routes.
    # Redirect the user back to the previous page
    return redirect(request.referrer)


@app.route('/removeLastSectionFromChosenSections/<int:section_id>', methods=['POST'])
@roles_required('admin')
def removeLastSectionFromChosenSections(section_id):
    # Get the reference to the section from the ChosenSectionsForNewLine table
    chosen_section = ChosenSectionsForNewLine.query.filter_by(section_id=section_id).first()

    # Check if the reference exists
    if chosen_section is None:
        # Handle the error (this is just an example)
        return "Error: No section found with the given ID", 404

    # Remove the reference to the section from the ChosenSectionsForNewLine table
    db.session.delete(chosen_section)

    # Get the last section from the ChosenSectionsForNewLine table
    last_section = ChosenSectionsForNewLine.query.order_by(ChosenSectionsForNewLine.order.desc()).first()

    if last_section is None:
        # If there are no more sections in the ChosenSectionsForNewLine table, add all sections to the AvailableSectionsForNewLine table
        sections = Section.query.all()
    else:
        # Get all sections from the Section table where the startStation equals the endStation of the last section
        sections = Section.query.filter_by(startStation=last_section.section_rel.endStation).all()

    # Clear the AvailableSectionsForNewLine table
    AvailableSectionsForNewLine.query.delete()

    # Add the sections to the AvailableSectionsForNewLine table
    for i, section in enumerate(sections):
        available_section = AvailableSectionsForNewLine(section_id=section.id)
        db.session.add(available_section)

    # Commit the changes to the database
    db.session.commit()

    #This is necessary because the route can be accessed from multiple other routes.
    # Redirect the user back to the previous page
    return redirect(request.referrer)


@app.route('/newLineAdminEnterDetails', methods=['GET', 'POST'])
@roles_required('admin')
def newLineAdminEnterDetails():
    if request.method == 'POST':
        name_of_line = request.form['nameOfLine']
        chosen_sections = ChosenSectionsForNewLine.query.order_by(ChosenSectionsForNewLine.order).all()

        line = Line(nameOfLine=name_of_line)
        db.session.add(line)
        db.session.flush()  # This is needed to generate the id for the new Line

        for i, chosen_section in enumerate(chosen_sections):
            db.session.execute(line_sections.insert().values(line_id=line.id, section_id=chosen_section.section_id, order=i))

        db.session.commit()

        return redirect(url_for('index'))  # or wherever you want to redirect the user after creating the line

    else:
        chosen_sections = ChosenSectionsForNewLine.query.order_by(ChosenSectionsForNewLine.order).all()
        start_station = chosen_sections[0].section_rel.start_station_rel.nameOfStation if chosen_sections else None
        end_station = chosen_sections[-1].section_rel.end_station_rel.nameOfStation if chosen_sections else None
        return render_template('newLineAdminEnterDetails.html', start_station=start_station, end_station=end_station)


@app.route('/editLinesAdmin', methods=['GET', 'POST'])
@roles_required('admin')
def editLinesAdmin():
    if request.method == 'POST':
        line_id = request.form.get('line_id')
        line = Line.query.get(line_id)

        if line:
            db.session.delete(line)
            db.session.commit()

        return redirect(url_for('editLinesAdmin'))

    lines = Line.query.all()
    return render_template('editLinesAdmin.html', lines=lines)
 

@app.route('/editSingleLineAdminPrepareDB/<int:id>', methods=['GET'])
@roles_required('admin')
def editSingleLineAdminPrepareDB(id):
    # Get the line with the given ID
    line = Line.query.get(id)

    # Clear the AvailableSectionsForNewLine and ChosenSectionsForNewLine tables
    AvailableSectionsForNewLine.query.delete()
    ChosenSectionsForNewLine.query.delete()

    # Load the sections of the line into the ChosenSectionsForNewLine table
    for order, section in enumerate(line.sections):
        chosen_section = ChosenSectionsForNewLine(section_id=section.id, order=order)
        db.session.add(chosen_section)

    # Get the end station of the last section in the ChosenSectionsForNewLine table
    last_end_station = ChosenSectionsForNewLine.query.order_by(ChosenSectionsForNewLine.order.desc()).first().section_rel.end_station_rel

    # Load the sections where the start station equals the last end station into the AvailableSectionsForNewLine table
    available_sections = Section.query.filter_by(startStation=last_end_station.id).all()
    for section in available_sections:
        available_section = AvailableSectionsForNewLine(section_id=section.id)
        db.session.add(available_section)

    db.session.commit()

    return redirect(url_for('editSingleLineAdminSectionsAssistantFrontend', line_id=id))



@app.route('/editSingleLineAdminSectionsAssistantFrontend/<int:line_id>', methods=['GET'])
@roles_required('admin')
def editSingleLineAdminSectionsAssistantFrontend(line_id):
    # Get the line with the given ID
    line = Line.query.get(line_id)

    # Get the chosen sections and available sections for the line
    chosen_sections = ChosenSectionsForNewLine.query.all()
    available_sections = AvailableSectionsForNewLine.query.all()

    # Render the template and pass the line, chosen sections, and available sections to it
    return render_template('editSingleLineAdminSectionsAssistantFrontend.html', line=line, chosen_sections=chosen_sections, available_sections=available_sections)


@app.route('/editSingleLineChangeName/<int:line_id>', methods=['GET', 'POST'])
@roles_required('admin')
def editSingleLineChangeName(line_id):
    line = Line.query.get(line_id)
    if request.method == 'POST':
        name_of_line = request.form['nameOfLine']
        line.nameOfLine = name_of_line
        db.session.commit()
        return redirect(url_for('index'))  # or wherever you want to redirect the user after editing the line
    else:
        return render_template('editSingleLineChangeName.html', line_id=line_id, nameOfLine=line.nameOfLine)

        
        
@app.route('/deleteLineAdmin', methods=['POST'])
@roles_required('admin')
def deleteLineAdmin():
    line_id = request.form.get('line_id')
    line = Line.query.get(line_id)

    if line:
        db.session.delete(line)
        db.session.commit()

    return redirect(url_for('editLinesAdmin'))




@app.route('/register', methods=['GET', 'POST'])
@roles_required('admin')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        admin_role = Role.query.filter_by(name='admin').first()
        employee_role = Role.query.filter_by(name='employee').first()
        if form.is_admin.data:
            user.roles.append(admin_role)
        else:
            user.roles.append(employee_role)
        db.session.add(user)
        db.session.commit()
        flash('Benutzer angelegt')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/editUsersAdmin')
@roles_required('admin')
def editUsersAdmin():
    users = User.query.all()
    return render_template('editUsersAdmin.html', users=users)
from werkzeug.security import generate_password_hash

@app.route('/editSingleUser/<int:id>', methods=['GET', 'POST'])
@roles_required('admin')
def editSingleUser(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:  # check if a new password was provided
            user.password = generate_password_hash(form.password.data)  # update the password
        if form.is_admin.data:
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role not in user.roles:
                user.roles.append(admin_role)
        else:
            user.roles = [role for role in user.roles if role.name != 'admin']
        db.session.commit()
        return redirect(url_for('editUsersAdmin'))
    form.is_admin.data = any(role.name == 'admin' for role in user.roles)
    return render_template('editSingleUser.html', form=form)


@app.route('/deleteSingleUser/<int:id>', methods=['POST'])
@roles_required('admin')
def deleteSingleUser(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('editUsersAdmin'))


@app.route('/viewLinesEmployee')
@roles_required('employee')
def viewLinesEmployee():
    lines = Line.query.all()  # get all lines
    for line in lines:
        line.valid_events_exist = any(section.events for section in line.sections)
    return render_template('viewLinesEmployee.html', lines=lines)

@app.route('/viewSpecificSectionEmployee/<int:line_id>')
@roles_required('employee')
def viewSpecificSectionEmployee(line_id):
    line = Line.query.get(line_id)  # get the specific line
    sections = line.sections  # get the sections of the line
    return render_template('viewSpecificSectionEmployee.html', sections=sections, now=datetime.utcnow().date())

@app.route('/viewStationsEmployee')
@roles_required('employee')
def viewStationsEmployee():
    stations = Station.query.all()  # get all stations
    return render_template('viewStationsEmployee.html', stations=stations)