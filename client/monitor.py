import json
from app import app, db
from app.models import User, Notification, Rule
from datetime import datetime, timedelta
from classes import notification_class, user_class, empty_class
from dbfunctions import pvlistfromdb, update_db
from re import compile
from miscfunctions import testpv, makepvpool, notification2server
from iofunctions import write, current_path
from time import sleep

def evaluate(debug=False, exclude=[]):
    # dbfunctions.update_fullpvlist()
    # fullpvlist = dbfunctions.pvlistfromdb()
    i, j, l = 0, 0, 0
    fullpvlist = pvlistfromdb()
    l = 0
    while True:
        if 'iteration' not in exclude:
            if debug == True:
                print('>>> Iteration', l)
        notifications_raw = db.session.query(Notification).all()
        pvpool = makepvpool(notifications_raw, fullpvlist) #dict with pv : value
        if 'pvpool' not in exclude:
            if debug == True:
                print('>>> pvpool:')
                print(pvpool)
        for data in notifications_raw: #for each notification
            pvlist_local = []
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
            if 'notification' not in exclude:
                if debug == True:
                    print('>>> notification:')
                    attrs = vars(notification)
                    print(attrs)
                    print('>>> user:')
                    attrs = vars(user)
                    print(attrs)

            # datetime_created = datetime.strptime(notification.created, '%Y-%m-%d %H:%M')
            n = json.loads(notification.notification)
            k = 0
            toEval = ''
            notificationCore = empty_class()
            for item in n['notificationCores']: #build notificationCore / each line of notification
                nC = 'notificationCore' + str(k)
                if k == 0: #variables for first notificationCore
                    comp_regex = compile(item[nC]['pv'])
                    notificationCore.pv = list(filter(comp_regex.match, fullpvlist))
                    notificationCore.rule = item[nC]['rule']
                    toDebug = [notificationCore.pv, notificationCore.rule]
                    if 'LL' not in item[nC]['rule']:
                        notificationCore.limit = item[nC]['limit']
                        toDebug.append(notificationCore.limit)
                    else:
                        notificationCore.limitLL = item[nC]['limitLL']
                        notificationCore.limitLU = item[nC]['limitLU']
                        toDebug.append(notificationCore.limitLL)
                        toDebug.append(notificationCore.limitLU)
                    notificationCore.subrule = item[nC]['subrule']
                else: #variables for notificationCore1 and so on
                    comp_regex = compile(item[nC]['pv' + str(k)])
                    notificationCore.pv = list(filter(comp_regex.match, fullpvlist))
                    notificationCore.rule = item[nC]['rule' + str(k)]
                    toDebug = [notificationCore.pv, notificationCore.rule]
                    if 'LL' not in item[nC]['rule' + str(k)]:
                        notificationCore.limit = item[nC]['limit' + str(k)]
                        toDebug.append(notificationCore.limit)
                    else:
                        notificationCore.limitLL = item[nC]['limitLL' + str(k)]
                        notificationCore.limitLU = item[nC]['limitLU' + str(k)]
                        toDebug.append(notificationCore.limitLL)
                        toDebug.append(notificationCore.limitLU)
                    notificationCore.subrule = item[nC]['subrule' + str(k)]
                #print(notificationCore.pv, notificationCore.rule)
                k += 1
                #print('======== pv/rule/limit/subrule ========')
                #print(vars(notificationCore))
                if debug == True:
                    print('< pv, rule, limit >')
                    print(toDebug)
                r = testpv(notificationCore, pvpool, user, fullpvlist)
                if 'testpv' not in exclude:
                    if debug == True:
                        print('>>> testpv result:')
                        print(r)
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
            if notification.last_sent != None:
                notification.sent = True
            else:
                notification.sent = False
            interval = timedelta(minutes=int(notification.interval))
            now = datetime.now()
            if now <= notification.expiration: #if notification didnt expire
                if debug == True:
                    print(">>> Notification didn't expire.")
                var = pvlist_local[0][1][0]
                owner = pvlist_local[0][-1].username
                if notification.sent == True: #was sent
                    if debug == True:
                        print('>>> Notification already sent in', notification.last_sent)
                    if now > (notification.last_sent + interval):
                        if notification.persistence == 'YES': #persistence YES
                            if debug == True:
                                print('>>> Notification is persistent.')
                                print('Eval result:', eval(toEval))
                            if eval(toEval):
                                if 'pvlist' not in exclude:
                                    if debug == True:
                                        print('pvlist:', pvlist_local)
                                ans = notification2server(pvlist_local, pvpool)
                                if debug == True:
                                    print('notification2server result:', ans)
                                if ans == 'ok':
                                    log = str(datetime.now()) + ' message to ' + owner + \
                                        ' sent to server. PV: ' + var + '\n\r'
                                    fullpath = current_path('log.txt')
                                    r = write(fullpath, log)
                                    if debug == True:
                                        print('>>> SMS notification sent.')
                                    if r != 'ok':
                                        if debug == True:
                                            print('>>> SMS notification not sent due error.')
                                        print(r)
                                    else:
                                        id = notification.id
                                        aux = update_db('Notification', id, 'last_sent', now)
                                        if debug == True:
                                            if aux == 'ok':
                                                print('>>> last_sent database field updated.')
                                            else:
                                                print('>>> error writing last _sent database field:', aux)
                                else:
                                    if debug == True:
                                        print(ans)
                        else: #persistence NO
                            if debug == True:
                                print('>>> Notification not persistent.')
                            if notification.sent == False: #not sent
                                evaluation = eval(toEval)
                                if debug == True:
                                    print('>>> Notification never sent before.')
                                    print('Eval result:', evaluation)
                                if evaluation:
                                    ans = notification2server(pvlist_local, pvpool)
                                    if debug == True:
                                        print('notification2server result:', ans)
                                    if ans == 'ok':
                                        log = str(datetime.now()) + ' message to ' + owner + \
                                            ' sent to server. PV: ' + var + '\n\r'
                                        fullpath = current_path('log.txt')
                                        r = write(fullpath, log)
                                        if r != 'ok':
                                            if debug == True:
                                                print('>>> SMS notification not sent due error.')
                                            print(r)
                                        else:
                                            if debug == True:
                                                print('>>> SMS notification sent')
                                            id = notification.id
                                            aux = update_db('Notification', id, 'last_sent', now)
                                            if debug == True:
                                                if aux == 'ok':
                                                    print('>>> last_sent database field updated.')
                                                else:
                                                    print('>>> error writing last _sent database field:', aux)
                                    else:
                                        if debug == True:
                                            print(ans)
                else: #wasnt sent yet
                    evaluation = eval(toEval)
                    if debug == True:
                        print('>>> Notification never sent before.')
                        print('Eval result:', evaluation)
                    if evaluation:
                        ans = notification2server(pvlist_local, pvpool)
                        if debug == True:
                            print('notification2server result:', ans)
                        if ans == 'ok':
                            log = str(now) + ' message to ' + owner + \
                                ' sent to server. PV: ' + var + '\n\r'
                            fullpath = current_path('log.txt')
                            r = write(fullpath, log)
                            if r != 'ok':
                                if debug == True:
                                    print('>>> SMS notification not sent due error.')
                                print(r)
                            else:
                                if debug == True:
                                    print('>>> SMS notification sent.')
                                id = notification.id
                                aux = update_db('Notification', id, 'last_sent', now)
                                if debug == True:
                                    if aux == 'ok':
                                        print('>>> last_sent database field updated.')
                                    else:
                                        print('error writing last _sent database field:', aux)
                        else:
                            if debug == True:
                                print(ans)
        sleep(10)
        if debug == True:
            l += 1  
            # break   
            # if j >= len(notifications_raw) - 1:
            #    print(j)
            # j += 1
exclude = ['iteration',\
            'pvpool',\
            'notification',\
            'testpv',\
            'pvlist',\
            '']
evaluate()