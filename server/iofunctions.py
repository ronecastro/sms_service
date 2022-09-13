from modem_usb import Modem
from os import path
import configparser, socket, pickle

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
    err = ''
    while True:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the port
        server_address = (ip, port)
        sock.bind(server_address)
        sock.listen()
        conn, addr = sock.accept()
        # print(f"Connected by {addr}")
        data = b''
        try:
            data += conn.recv(1024)
            conn.sendall(data)
        except Exception as e:
            err += e
            return 'error at conn.recv: ', e
        finally:
            sock.close()
        rcvd_data = pickle.loads(data)
        print(rcvd_data)

ip = str(fromcfg('ADDRESS', 'ip'))
port = int(fromcfg('ADDRESS', 'port'))
msg = tcpsock_server(ip, port)
print(msg)
# 19996018157
# print(sendsms(mode='direct', number='19997397443', msg='test'))