from modem_usb import Modem

def sendsms(mode, number, msg):
    try:
        modem = Modem(path='/dev/ttyUSB0')
    except Exception as e:
        return e
    ans = modem.initialize()
    if 'OK' in ans:
        ans = modem.sendsms(mode=mode, number=number, msg=msg)
        modem.closeconnection()
        if 'OK' in ans:
            return ans
        else:
            return 'error sending message: ' + ans
    else:
        modem.closeconnection()
        return 'error on modem initialization: ' + ans


# print(sendsms(mode='direct', number='19996018157', msg='test'))