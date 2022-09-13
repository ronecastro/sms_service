import configparser, socket, pickle
from os import path

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
        fullpath = current_path('config.cfg')
        config = configparser.RawConfigParser()
        # dir_path = path.dirname(path.realpath(__file__), )
        # config_path = path.join(dir_path, 'config.cfg')
        config.read_file(open(fullpath)) 
        r = config.get(section,key)
    except:
        return "error on reading 'config.cfg' file"
    return r

def write(filepath, msg):
    try:
        f = open(filepath, 'a')
        f.write(msg)
        f.close
        return 'ok'
    except Exception as e:
        return e


def tcpsock_client(msg, ip='locahost', port=5007):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    data = b''
    s = ''
    conn = ''
    rcvd_data = b''

    address = (ip, port)
    try: #sock connect
        sock.connect(address)
    except Exception as e:
        return "error on 'connect':", e

    try:# sock send msg
        send_data = pickle.dumps(msg)
        s = sock.sendall(send_data)
    except Exception as e:
        return "error on 'sendall':", e

    if s == None:
        try:
            data = sock.recv(1024)
        except Exception as e:
            return 'error', e

        rcvd_data = pickle.loads(data)
        if rcvd_data == msg:
            sock.close()
            return 'ok'
        else:
            sock.close()
            return 'error on received echo msg'
    else:
        sock.close()
        return 'error on sending msg to server'

# ip = str(fromcfg('ADDRESS', 'ip'))
# port = int(fromcfg('ADDRESS', 'port'))
# print(tcpsock_client('oyeah', ip, port))