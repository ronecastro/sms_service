import configparser, socket, pickle
from os import path
from classes import socketClient

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
    address = (ip, port)
    client = socketClient(address)
    sock = client.create_socket()
    ans = client.connect(sock)
    if ans == 'ok':
        ans = client.send_data(sock, msg)
    else:
        return 'error on connecting to server', ans
    if ans == 'ok':
        ans = client.receive_data(sock, 1024)
        if ans == msg:
            ans = 'ok'
        else:
            client.close(sock)
            return 'error on receiving data', ans
    client.close(sock)
    return ans

# ip = str(fromcfg('ADDRESS', 'ip'))
# port = int(fromcfg('ADDRESS', 'port'))
# print(tcpsock_client('oyeah', ip, port))