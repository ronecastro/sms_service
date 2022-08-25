from cmath import inf
from wsgiref.validate import validator
from app import app, db
from app.models import User, Notification, Rule
from flask import render_template, flash, redirect, url_for, request, g, session, Response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, RuleForm, NotificationForm
from datetime import datetime
import json, re
from dbfunctions import searchdb

#primary light blue
#secondary light grey
#success green
#danger red
#warning yellow
#info blueish green?!
#light light grey text no background
#dark dark grey

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    return searchdb(request.args.get('q'))

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        current_user.username="Guest User"
    return render_template('index.html', title='Home')

@app.route('/user/<username>', methods=['GET'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = LoginForm()
    session['last_url'] = url_for('profile', username=username)
    session['login_required'] = True
    return render_template('profile.html', form=form, user=user , title='Profile')

@app.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def profile_edit(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = RegistrationForm(user=user, custom_validation=True, email=user.email, phone=user.phone)
    form.__delitem__("password")
    form.__delitem__("password2")
    form.__delitem__("username")
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('profile', username=user.username))
        if form.validate():
            user.email = form.email.data
            user.phone = form.phone.data
            db.session.commit()
            flash("Successful editing!", "success")
            return render_template('profile.html', username=user.username, user=user, title='Profile')
        else:
            pass
    session['last_url'] = url_for('profile_edit', username=username)
    session['login_required'] = True
    return render_template('profile-edit.html', form=form, user=user, title='Edit Profile')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!', 'warning')
            return redirect(url_for('index'))
        login_user(user, remember=form.remember_me.data)
        session['_flashes'].clear()
        flash('Login successfull!', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/login-modal', methods=['GET', 'POST'])
def login_modal():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == "POST":
        if form.validate():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password!', 'warning')
                return redirect(url_for('index'))
            login_user(user, remember=form.remember_me.data)
            flash('Login successfull!', 'success')
            if session.get('last_url') != None:
                return redirect(url_for(session['last_url'].rsplit('/')[-1]))
            else:
                return redirect(url_for('index'))
        else:
            flash('Login failed!', 'warning')
            return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('login-modal.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm("0") # any argument to satisfy init function
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Congratulations, you are now a registered user!', "success")
        return redirect(url_for('index'))
    session['last_url'] = url_for('register')
    session['login_required'] = False
    return render_template('register.html', title='Register', form=form)

@app.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    users =  db.session.query(User).all()
    if request.method == "POST":
        action = request.form['action']
        if action == 'delete':
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            for i in checked_list:
                user = User.query.filter_by(id=i).first()
                db.session.delete(user)
                db.session.commit()
            return redirect(url_for('accounts'))
    session['last_url'] = url_for('accounts')
    session['login_required'] = True
    return render_template('accounts.html', users=users, title='Accounts')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have logged out!', "success")
    if session.get('login_required') != None:
        if session['login_required'] == False:
            last_page = session['last_url'].rsplit('/')[-1]
            return redirect(url_for(last_page))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/forgot')
def forgot():
    return render_template('forgot.html', title='Password Recovery')

@app.route('/notifications', methods=['GET', 'POST'])
def notifications():
    print('notification session', session)
    if request.method == "POST":
        action = request.form['action']
        if action == 'add':
            return redirect(url_for('notifications_add'))
        if action == 'edit':
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            if (len(checked_list) > 1):
                flash('Select only one notification to edit!', 'warning')
            elif (len(checked_list) == 0):
                flash('Select one notification to edit!', 'warning')
            else:
                id = checked_list[0]
                return redirect(url_for('notifications_edit', id=id))
        if action == 'delete':
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            if len(checked_list) > 0:
                for item in checked_list:
                    notification = db.session.query(Notification).filter_by(id=item).first()
                    db.session.delete(notification)
                    db.session.commit()
                flash('Notification(s) deleted!', 'success')
                return redirect(url_for('notifications'))
    user = current_user
    #rule = Rule.query.filter_by(id=checked_list[0]).first()
    users = db.session.query(User).all()
    #notifications = db.session.query(Notification).all()
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            notifications = db.session.query(Notification).all()
        else:
            notifications = db.session.query(Notification).filter_by(user_id=user.id).all()
    else:
        notifications = db.session.query(Notification).all()
    session['last_url'] = url_for('notifications')
    session['login_required'] = False
    return render_template('notifications.html', users=users, notifications=notifications, title='Notifications')

@app.route('/notifications/add', methods=['GET', 'POST'])
@login_required
def notifications_add():
    errors = []
    rules = db.session.query(Rule).all()
    user = current_user
    emsg = ''
    if request.method == "POST":
        requestJson = json.dumps(request.get_json(force=True))
        requestJson_load = json.loads(requestJson)
        print('requestJson_load', requestJson_load)
        expiration = requestJson_load['expiration']
        interval = requestJson_load['interval']
        pv = requestJson_load['notificationCores'][0]['notificationCore0']['pv']
        rule = requestJson_load['notificationCores'][0]['notificationCore0']['rule']
        limit = requestJson_load['notificationCores'][0]['notificationCore0']['limit']
        if not expiration:
            errors.append('expiration')
            emsg += 'Set expiration! '
        if not interval.isnumeric:
            errors.append('interval')
            emsg += 'Interval must be numeric! '
        if not pv:
            errors.append('pv')
            emsg += 'Set PV! '
        if not rule:
            errors.append('rule')
            emsg += "Set rule! "
        if not limit.isnumeric():
            errors.append('limit')
            emsg += 'Limit must be numeric! '
        if len(errors) == 0:
            notification = Notification(
                user_id = user.id,
                notification=requestJson)
            db.session.add(notification)
            db.session.commit()
            flash('Notification added!', 'success')
            return url_for('notifications')
        else:
            r = ({'warning': True}, 205, {'ContentType':'application/text'}) #tuple response format
            flash(emsg, 'warning')
            return r
    session['last_url'] = url_for('notifications_add')
    session['login_required'] = True
    return render_template('notifications-add.html', rules=rules, title='Add Notification')

@app.route('/notifications/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def notifications_edit(id):
    if request.method == "POST":
        action = request.form
        requestJson = json.dumps(request.get_json(force=True))
        notification = db.session.query(Notification).filter_by(id=id).first()
        notification.notification = requestJson
        db.session.commit()
        flash("Notification edited sucessfully!", "success")
        return redirect(url_for('notifications'))
    rules = db.session.query(Rule).all()
    notification = db.session.query(Notification).filter_by(id=id).all()
    session['last_url'] = url_for('notifications_edit', id=id)
    session['login_required'] = True
    return render_template('notifications-edit.html', id=id, rules=rules, \
        notification=notification, title='Edit Notification')

@app.route('/notifications/cancel', methods=['GET', 'POST'])
@login_required
def notifications_cancel():
    return redirect(url_for('notifications'))

@app.route('/rules', methods=['GET', 'POST'])
def rules():
    rules = db.session.query(Rule).all()
    session['last_url'] = url_for('rules')
    session['login_required'] = False
    return render_template('rules.html', rules=rules, title='Rules Configuration')

@app.route('/rules/configuration', methods=['GET', 'POST'])
@login_required
def rules_configure():
    g.id = None
    if request.method == "POST":
        action = request.form['action']
        if action == 'add':
            return redirect(url_for('rules_add'))
        if action == 'edit':
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            if len(checked_list) > 1:
                flash("Select only one rule to edit!", "warning")
                return redirect(url_for('rules_configure'))
            if len(checked_list) == 0:
                flash("Select one rule to edit!", "warning")
                return redirect(url_for('rules_configure'))
            rule = Rule.query.filter_by(id=checked_list[0]).first()
            return redirect(url_for('rules_edit', id=rule.id))
        if action == 'delete':
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            for i in checked_list:
                rule = Rule.query.filter_by(id=i).first()
                db.session.delete(rule)
                db.session.commit()
            flash("Rule(s) deleted!", "success")
            return redirect(url_for('rules_configure'))
    rules = db.session.query(Rule).all()
    session['last_url'] = url_for('rules_configure')
    session['login_required'] = True
    return render_template('rules-configure.html', rules=rules, title='Rules Configuration')

@app.route('/rules/configuration/add', methods=['GET', 'POST'])
@login_required
def rules_add():
    g.id = None
    if current_user.is_authenticated != True:
        return redirect(url_for('index'))
    form = RuleForm()
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('rules_configure'))
        if form.validate_on_submit():
            rule = Rule(rule=form.rule.data, description=form.description.data)
            db.session.add(rule)
            db.session.commit()
            flash("Rule added!", "success")
            return redirect(url_for('rules_configure'))
    session['last_url'] = url_for('rules_add')
    session['login_required'] = True
    return render_template('rules-add.html', form=form, title='Rules Configuration')

@app.route('/rules/configuration/edit/<id>', methods=['GET', 'POST'])
@login_required
def rules_edit(id):
    rule = Rule.query.filter_by(id=id).first()
    form = RuleForm(rule=rule.rule, description=rule.description)
    if request.method == "POST":
        g.id = id
        if form.cancel.data:
            return redirect(url_for('rules_configure'))
        if form.validate_on_submit():
            rule.rule = form.rule.data
            rule.description = form.description.data
            db.session.commit()
            flash("Successful editing!", "success")
            return redirect(url_for('rules_configure'))
    session['last_url'] = url_for('rules_edit', id=id)
    session['login_required'] = True
    return render_template('rules-edit.html', form=form, rule=rule, title='Rules Configuration')
