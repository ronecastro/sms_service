from modem_usb import Modem
from os import path
from classes import socketServer
import configparser


def current_path(file=None):
    try:
        dir_path = path.dirname(path.realpath(__file__), )
        if file != None:
            config_path = path.join(dir_path, file)
            return config_path
        else:
            return dir_path
    except Exception as e:
        return e

def fromcfg(section,key):
    try:
        config = configparser.RawConfigParser()
        dir_path = path.dirname(path.realpath(__file__), )
        config_path = path.join(dir_path, 'config.cfg')
        config.read_file(open(config_path)) 
        r = config.get(section,key)
    except:
        return "error on reading 'config.cfg' file"
    return r

def sendsms(mode, number, msg):
    try:
        modem = Modem(path='/dev/ttyUSB0', debug=True)
    except Exception as e:
        return 'error setting modem: ', e
    ans = modem.initialize()
    if ('OK' in ans) and ('nOK' not in ans):
        ans = modem.sendsms(mode=mode, number=number, msg=msg)
        modem.closeconnection()
        if ('OK' in ans) and ('nOK' not in ans):
            return 'OK'
        else:
            return 'error sending message: ', ans
    else:
        modem.closeconnection()
        return 'error on modem initialization: ', ans

def tcpsock_server(ip='localhost', port=5007):
    address = (ip, port)
    server = socketServer(address)
    sock = server.create_socket()
    ans = server.bind_address(sock)
    ans = server.listen(sock)
    conn, addr = server.accept_connection(sock)
    data = server.receive_data(conn, 1024, echo=True)
    print(data)


# ip = str(fromcfg('ADDRESS', 'ip'))
# port = int(fromcfg('ADDRESS', 'port'))
# msg = tcpsock_server(ip, port)
# print(msg)
# 19996018157
# print(sendsms(mode='direct', number='19997397443', msg='test'))