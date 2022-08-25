import json
from app import app, db
from app.models import User, Notification, Rule
from datetime import datetime, timedelta
from classes import notification_class, user_class, empty_class
from dbfunctions import pvlistfromdb
from re import compile
from miscfunctions import testpv, makepvpool, sendnotification

def evaluate():
    # dbfunctions.update_fullpvlist()
    # fullpvlist = dbfunctions.pvlistfromdb()
    i, j = 0, 0
    fullpvlist = pvlistfromdb()
    while True:
        now = datetime.now()
        notifications_raw = db.session.query(Notification).all()
        pvpool = makepvpool(notifications_raw, fullpvlist) #dict with pv : value
        # print(pvpool)
        for data in notifications_raw: #for each notification
            pvlist_local = []
            pos = notifications_raw.index(data)
            user_raw = db.session.query(User).filter_by(id=data.user_id).first()

            notification = notification_class(id = data.id, \
                            user_id = data.user_id, \
                            notification = data.notification, \
                            last_sent = data.last_sent)
            n = notification.json()
            notification.created = n['created']
            notification.expiration = datetime.strptime(n['expiration'], '%Y-%m-%d %H:%M')
            notification.interval = n['interval']
            notification.persistence = n['persistence']

            user = user_class(id = user_raw.id, \
                    username = user_raw.username, \
                    email = user_raw.email,\
                    phone = user_raw.phone)

            datetime_created = datetime.strptime(notification.created, '%Y-%m-%d %H:%M')
            #print('notification', notification.notification)
            n = json.loads(notification.notification)
            #print(len(n['notificationCores']))
            k = 0
            toEval = ''
            notificationCore = empty_class()
            for item in n['notificationCores']: #build notificationCore / each line of notification
                nC = 'notificationCore' + str(k)
                if k == 0: #variables for first notificationCore
                    comp_regex = compile(item[nC]['pv'])
                    notificationCore.pv = list(filter(comp_regex.match, fullpvlist))
                    notificationCore.rule = item[nC]['rule']
                    if 'LL' not in item[nC]['rule']:
                        notificationCore.limit = item[nC]['limit']
                    else:
                        notificationCore.limitLL = item[nC]['limitLL']
                        notificationCore.limitLU = item[nC]['limitLU']
                    notificationCore.subrule = item[nC]['subrule']
                else: #variables for notificationCore1 and so on
                    comp_regex = compile(item[nC]['pv' + str(k)])
                    notificationCore.pv = list(filter(comp_regex.match, fullpvlist))
                    notificationCore.rule = item[nC]['rule' + str(k)]
                    if 'LL' not in item[nC]['rule' + str(k)]:
                        notificationCore.limit = item[nC]['limit' + str(k)]
                    else:
                        notificationCore.limitLL = item[nC]['limitLL' + str(k)]
                        notificationCore.limitLU = item[nC]['limitLU' + str(k)]
                    notificationCore.subrule = item[nC]['subrule' + str(k)]
                #print(notificationCore.pv, notificationCore.rule)
                k += 1
                #print('======== pv/rule/limit/subrule ========')
                #print(vars(notificationCore))
                r = testpv(notificationCore, pvpool, user, fullpvlist)
                for y in r:
                    pvlist_local.append(y) #build list with pv rule test
                if len(notificationCore.pv) == 1:
                    toEval += str(r[-1][0]) + ' ' + notificationCore.subrule.lower() + ' '
                else:
                    toEval = '('
                    p = 0
                    for t in notificationCore.pv:
                        if notificationCore.pv.index(t) < len(notificationCore.pv)-1:
                            toEval += str(r[p][0]) + ' ' + 'or' + ' '
                        else:
                            toEval += str(r[p][0]) + ')'
                        p += 1
                #print('r', r)
                #print('toEval', toEval)
            #print('======== marker ========')
            #print(notification.id, eval(toEval))
            #print(notification.last_sent)
            if notification.last_sent != None:
                notification.sent = True
            else:
                notification.sent = False
            #print('pvlist_local', pvlist_local)
            interval = timedelta(minutes=int(notification.interval))
            if now <= notification.expiration: #if notification didnt expire
                if notification.sent == True: #was sent
                    #interval time has already passed
                    if now > (notification.last_sent + interval):
                        if notification.persistent == 'YES': #persistence YES
                            if eval(toEval):
                                msg = ''
                                #print('eval sent persistence YES', toEval)
                                sendnotification(pvlist_local, pvpool)
                        else: #persistence NO
                            if notification.sent == False: #not sent
                                msg = ''
                                #print('eval sent persistence NO', toEval)
                                sendnotification(pvlist_local, pvpool)
                else: #wasnt sent yet
                    if eval(toEval):
                        msg = ''
                        #print('eval not sent', toEval)
                        sendnotification(pvlist_local, pvpool)
                        

            if j >= len(notifications_raw) - 1:
                exit()
            j += 1

evaluate()