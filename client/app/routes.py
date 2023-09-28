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
from miscfunctions import get_enum_list

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

@app.route('/gethint', methods=['GET'])
def gethint():
    if request.method == 'GET':
        pv = request.args['pv']
        if pv:
            hint = get_enum_list(pv)
            return str(hint)
        else:
            return 'None'

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
        phone = form.phone.data
        pattern = "^[+][\d]+$"
        if re.match(pattern, phone):
            if form.validate():
                user.email = form.email.data
                user.phone = form.phone.data
                db.session.commit()
                flash("Successful editing!", "success")
                return render_template('profile.html', username=user.username, user=user, title='Profile')
            else:
                pass
        else:
            flash('Please use phone only with "+" sign and numbers!', 'warning')
            return redirect(request.url)
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
        try:
            session['_flashes'].clear()
        except Exception as e:
            pass
        login_user(user, remember=form.remember_me.data)
        session['last_url'] = '/sms_service/index'
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
                try:
                    return redirect(url_for(session['last_url'].rsplit('/')[-1]))
                except Exception as e:
                    return redirect(url_for('index'))
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
        phone=(form.phone.data).replace("-","").replace(" ","")
        user = User(username=form.username.data, email=form.email.data, phone=phone)
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
    # print('notification session', session)
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
    # print(notifications)
    return render_template('notifications.html', users=users, notifications=notifications, title='Notifications')

@app.route('/notifications/add', methods=['GET', 'POST'])
@login_required
def notifications_add():
    errors = []
    rules = db.session.query(Rule).all()
    user = current_user
    emsg = ''
    if request.method == "POST":
        action = request.form
        requestJson = json.dumps(request.get_json(force=True))
        requestJson_load = json.loads(requestJson)
        # print(requestJson_load)
        expiration = requestJson_load['expiration']
        interval = requestJson_load['interval']
        nc = requestJson_load['notificationCores']
        limit = '0'
        limitLL = '0'
        limitLU = '0'
        for index in range(len(nc)):
            keys = requestJson_load['notificationCores'][index]['notificationCore'+str(index)].items()
            # print(dict(keys))
            if index == 0:
                pv = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['pv']
                rule = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['rule']
                if 'limitLL' in dict(keys):
                    limitLL = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLL']
                if 'limitLU' in dict(keys):
                    limitLU = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLU']
                else:
                    limit = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limit']
            else:
                pv = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['pv'+str(index)]
                rule = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['rule'+str(index)]
                aux = 'limitLL' + str(index)
                if aux in dict(keys):
                    limitLL = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLL'+str(index)]
                aux = 'limitLU' + str(index)
                if aux in dict(keys):
                    limitLU = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLU'+str(index)]
                else:
                    limit = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limit'+str(index)]
            if not expiration:
                if 'expiration' not in errors:
                    errors.append('expiration')
                if 'Set expiration! ' not in emsg:
                    emsg += 'Set expiration! '
            if not interval.isnumeric:
                if 'interval' not in errors:
                    errors.append('interval')
                if 'Interval must be numeric! ' not in emsg:
                    emsg += 'Interval must be numeric! '
            if int(interval) < 10:
                if 'interval10' not in errors:
                    errors.append('interval10')
                if 'Interval minimum is 10 minutes! ' not in emsg:
                    emsg += 'Interval minimum is 10 minutes! '
            if not pv:
                if 'pv' not in errors:
                    errors.append('pv')
                if 'Set PV! ' not in emsg:
                    emsg += 'Set PV! '
            if not rule:
                if 'rule' not in errors:
                    errors.append('rule')
                if "Set rule! " not in emsg:
                    emsg += "Set rule! "
            try:
                if float(limit):
                    pass
            except Exception as e:
                if 'limit' not in errors:
                    errors.append('limit')
                if 'Limit must be numeric!' not in emsg:
                    emsg += 'Limit must be numeric! '
            # if not limit.isnumeric() and limit:
            #     if 'limit' not in errors:
            #         errors.append('limit')
            #     if 'Limit must be numeric!' not in emsg:
            #         emsg += 'Limit must be numeric! '
            if not limit:
                if 'limit' not in errors:
                    errors.append('limit')
                if 'Set Limit of' not in emsg:
                    emsg += 'Set Limit of ' + pv + '! '
            try:
                if float(limitLL):
                    pass
            except Exception as e:
                if 'limitLL' not in errors:
                    errors.append('limitLL')
                if 'Limit LL must be numeric!' not in emsg:
                    emsg += 'Limit LL must be numeric! '
            # if not limitLL.isnumeric() and limitLL:
            #     if 'limitLL' not in errors:
            #         errors.append('limitLL')
            #     if 'Limit LL must be numeric!' not in emsg:
            #         emsg += 'Limit LL must be numeric! '
            if not limitLL:
                if 'limitLL' not in errors:
                    errors.append('limitLL')
                if 'Set Limit LL! ' not in emsg:
                    emsg += 'Set Limit LL of ' + pv + '! '
            try:
                if float(limitLU):
                    pass
            except Exception as e:
                if 'limitLU' not in errors:
                    errors.append('limitLU')
                if 'Limit LU must be numeric!' not in emsg:
                    emsg += 'Limit LU must be numeric! '
            # if not limitLU.isnumeric() and limitLU:
            #     if 'limitLU' not in errors:
            #         errors.append('limitLU')
            #     if 'Limit LU must be numeric!' not in emsg:
            #         emsg += 'Limit LU must be numeric! '
            if not limitLU:
                if 'limitLU' not in errors:
                    errors.append('limitLU')
                if 'Set Limit LU of' not in emsg:
                    emsg += 'Set Limit LU of' + pv + '! '
            # print(type(limit))
            # print(limitLL)
            # print(limitLU)
            # print(index)
        if len(errors) == 0:
            user_db = db.session.query(User).filter_by(username=user.username).first()
            user_id = user_db.id
            notification = Notification(
                user_id = user_id,
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
    errors = []
    emsg = ''
    if request.method == "POST":
        action = request.form
        requestJson = json.dumps(request.get_json(force=True))
        requestJson_load = json.loads(requestJson)
        # print(requestJson_load)
        expiration = requestJson_load['expiration']
        interval = requestJson_load['interval']
        nc = requestJson_load['notificationCores']
        limit = '0'
        limitLL = '0'
        limitLU = '0'
        for index in range(len(nc)):
            keys = requestJson_load['notificationCores'][index]['notificationCore'+str(index)].items()
            # print(dict(keys))
            if index == 0:
                pv = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['pv']
                rule = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['rule']
                if 'limitLL' in dict(keys):
                    limitLL = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLL']
                if 'limitLU' in dict(keys):
                    limitLU = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLU']
                else:
                    limit = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limit']
            else:
                pv = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['pv'+str(index)]
                rule = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['rule'+str(index)]
                aux = 'limitLL' + str(index)
                if aux in dict(keys):
                    limitLL = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLL'+str(index)]
                aux = 'limitLU' + str(index)
                if aux in dict(keys):
                    limitLU = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limitLU'+str(index)]
                else:
                    limit = requestJson_load['notificationCores'][index]['notificationCore'+str(index)]['limit'+str(index)]
            if not expiration:
                if 'expiration' not in errors:
                    errors.append('expiration')
                if 'Set expiration! ' not in emsg:
                    emsg += 'Set expiration! '
            if not interval.isnumeric:
                if 'interval' not in errors:
                    errors.append('interval')
                if 'Interval must be numeric! ' not in emsg:
                    emsg += 'Interval must be numeric! '
            if int(interval) < 10:
                if 'interval10' not in errors:
                    errors.append('interval10')
                if 'Interval minimum is 10 minutes! ' not in emsg:
                    emsg += 'Interval minimum is 10 minutes! '
            if not pv:
                if 'pv' not in errors:
                    errors.append('pv')
                if 'Set PV! ' not in emsg:
                    emsg += 'Set PV! '
            if not rule:
                if 'rule' not in errors:
                    errors.append('rule')
                if "Set rule! " not in emsg:
                    emsg += "Set rule! "
            try:
                if float(limit):
                    pass
            except Exception as e:
                if 'limit' not in errors:
                    errors.append('limit')
                if 'Limit must be numeric!' not in emsg:
                    emsg += 'Limit must be numeric! '
            # if not limit.isnumeric() and limit:
            #     if 'limit' not in errors:
            #         errors.append('limit')
            #     if 'Limit must be numeric!' not in emsg:
            #         emsg += 'Limit must be numeric! '
            if not limit:
                if 'limit' not in errors:
                    errors.append('limit')
                if 'Set Limit of' not in emsg:
                    emsg += 'Set Limit of ' + pv + '! '
            try:
                if float(limitLL):
                    pass
            except Exception as e:
                if 'limitLL' not in errors:
                    errors.append('limitLL')
                if 'Limit LL must be numeric!' not in emsg:
                    emsg += 'Limit LL must be numeric! '
            # if not limitLL.isnumeric() and limitLL:
            #     if 'limitLL' not in errors:
            #         errors.append('limitLL')
            #     if 'Limit LL must be numeric!' not in emsg:
            #         emsg += 'Limit LL must be numeric! '
            if not limitLL:
                if 'limitLL' not in errors:
                    errors.append('limitLL')
                if 'Set Limit LL! ' not in emsg:
                    emsg += 'Set Limit LL of ' + pv + '! '
            try:
                if float(limitLU):
                    pass
            except Exception as e:
                if 'limitLU' not in errors:
                    errors.append('limitLU')
                if 'Limit LU must be numeric!' not in emsg:
                    emsg += 'Limit LU must be numeric! '
            # if not limitLU.isnumeric() and limitLU:
            #     if 'limitLU' not in errors:
            #         errors.append('limitLU')
            #     if 'Limit LU must be numeric!' not in emsg:
            #         emsg += 'Limit LU must be numeric! '
            if not limitLU:
                if 'limitLU' not in errors:
                    errors.append('limitLU')
                if 'Set Limit LU of' not in emsg:
                    emsg += 'Set Limit LU of' + pv + '! '
            # print(type(limit))
            # print(limitLL)
            # print(limitLU)
            # print(index)
        if len(errors) == 0:
            notification = db.session.query(Notification).filter_by(id=id).first()
            notification.notification = requestJson
            db.session.commit()
            flash("Notification edited sucessfully!", "success")
            return url_for('notifications')
        else:
            r = ({'warning': True}, 205, {'ContentType':'application/text'}) #tuple response format
            flash(emsg, 'warning')
            return r
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

# Many PVs
# {
# 'created': '2022-11-15 17:02', 'expiration': '2022-11-01 10:55', 'interval': '61', 'persistence': 'YES',
# 'notificationCores':
# [
# {'notificationCore0': {'pv': '^LA-VA:H1VGC-02:RdPrs-2$', 'rule': 'pv < L', 'limit': '1e-8', 'subrule': 'OR'}},
# {'notificationCore1': {'pv1': '^LA-VA:H1VGC-03:RdPrs-1$', 'rule1': 'pv > L', 'limit1': '1e-8', 'subrule1': 'OR'}},
# {'notificationCore2': {'pv2': '^LA-VA:H1VGC-02:RdPrs-1$', 'rule2': 'pv > L', 'limit2': '1e-8', 'subrule2': ''}}
# ]
# }

# One PV
# {
# 'created': '2022-11-15 17:05', 'expiration': '2022-11-30 14:00', 'interval': '59', 'persistence': 'YES',
# 'notificationCores':
# [
# {'notificationCore0': {'pv': '^([T][S])(.+VA-CCG.+Pressure-Mon)$', 'rule': 'pv > L', 'limit': '1e-8', 'subrule': ''}}
# ]
# }
