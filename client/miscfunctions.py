from epics import caget, caget_many
import json, re, pickle
from classes import empty_class
from iofunctions import tcpsock_client, fromcfg

def testpv(notificationCore, pool, user, fullpvlist): #test pv using rule and limits
    pvlist = []
    truepv = []
    for n in notificationCore.pv: #notificationCore.pv is a list, n is pv name
        pv = (pool[n][0]) #value
        rule = notificationCore.rule
        subrule = notificationCore.subrule
        if 'LL' not in rule:
            L = float(notificationCore.limit)
            #print(pv, rule, L, eval(rule))
        else:
            LL = float(notificationCore.limitLL)
            LU = float(notificationCore.limitLU)
            #print(pv, rule, LL, LU, (eval(rule)))
        if (eval(rule)):
            pvlist.append(n)
            if 'LL' not in rule:
                #print('pv limit', n, pv, rule, L, eval(rule))
                truepv.append([True, pvlist, rule, notificationCore.limit, subrule, user])
            else:
                #print('pv limitLL/LU', n, pv, rule, LL, LU, eval(rule))
                truepv.append([True, pvlist, rule, notificationCore.limitLL,\
                                notificationCore.limitLU, subrule, user])
        else:
            # if 'LL' not in rule:
            #     print('pv limit', n, pv, rule, L, eval(rule))
            # else:
            #     print('pv limit', n, pv, rule, LL, LU, eval(rule))
            pvlist.append(n)
            truepv.append([False, pvlist, None, None, subrule, user])
        pvlist = []
    return truepv

def makepvpool(notifications_raw, fullpvlist): #buid dict with pv : value
    pvpool = {}
    pvs_ = []
    vals_ = []
    w = []
    j = 0
    for data in notifications_raw:
        i = 0
        notification = data.notification
        n = json.loads(notification)
        nC = 'notificationCore' + str(i)
        notificationCore = empty_class()
        notificationCore.pv = []
        for item in n['notificationCores']:
            #print(item) #item = each line of a notification (each pv)
            nC = 'notificationCore' + str(i)
            if i > 0:
                comp_regex = re.compile(item[nC]['pv' + str(i)])
                pvlist = list(filter(comp_regex.match, fullpvlist))
                for x in pvlist:
                    (notificationCore.pv).append([x, item])
            else:
                comp_regex = re.compile(item[nC]['pv'])
                pvlist = list(filter(comp_regex.match, fullpvlist))
                for x in pvlist:
                    (notificationCore.pv).append([x, item])
            i += 1
        for pv in notificationCore.pv:
           # print('pv', pv)
            if pv[0] not in pvpool:
                pvs_.append(pv[0])
                w.append(pv[1])
                try:
                    pass
                    #pvpool[pv[0]] = [caget(pv[0]), pv[1]]
                    #print('pv1', pv[1])
                except:
                    pass
        vals_ = caget_many(pvs_)
    for pv in pvs_:
        pvpool[pv] = [vals_[j], w[j]]
        j += 1
        #print[pvpool[pv[0]]]
    #print('pvpool', pvpool)
    #print('pvs_', pvs_)
    #print('vals_', vals_)
    return pvpool

def notification2server(pvlist, pvpool):
    header = 'WARNING!\n\r'
    body = ''
    sizetrue = 0
    pv = ''
    L = ''
    LL = ''
    LU = ''
    for i in pvlist:
        if i[0] == True:
            sizetrue += 1
    for item in pvlist: #for each pv in pvlist
        if item[0] == True:
            pv = item[1][0] #get pv name
            rule = item[2] #get rule
            if not 'LL' in rule: #for simple limit
                L = item[3]
                user = item[5]
                if sizetrue <= 2:
                    aux = rule.replace('pv', pv) + '\n\r'
                    aux = aux.replace('L', L)
                    aux += 'Last Value = ' + str(pvpool[pv][0]) + '\n\r'
                    body += aux
                else:
                    body = 'Many#\n\r'
            else: #for composite limit
                LL = item[3]
                LU = item[4]
                user = item[6]
                if sizetrue <= 2:
                    aux = 'PV = ' + pv + '\n\r'
                    aux += 'Rule = ' + rule + '\n\r'
                    aux += 'pv = ' + str(pvpool[pv][0]) + '\n\r'
                    aux += 'LL = ' + LL + '\n\r'
                    aux += 'LU = ' + LU + '\n\r'
                    body += aux
                else:
                    body = 'Many#\n\r'
    if 'Many#' in body:
        body = 'Many PVs reached their limits!\n\r'
        body += 'PVs alike: ' + pv + '\n\r'
    aux = (user.username, user.phone, user.email)
    msg = [aux, header + body]
    ip = str(fromcfg('ADDRESS', 'ip'))
    port = int(fromcfg('ADDRESS', 'port'))
    ans = tcpsock_client(msg, ip, port)
    if ans == 'ok':
        return 'ok'
    else:
        return 'error on tcpsock_client:', ans