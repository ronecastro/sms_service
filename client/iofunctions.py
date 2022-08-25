import configparser
from os import path
import socket

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

def tcpsock_client(msg):
    pass
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data = b''
    s = ''
    conn = ''

    server_ip = fromcfg('ADDRESS', 'server_ip')
    server_port = fromcfg('ADDRESS', 'server_port')
    server_address = (server_ip, server_port)

    try: #sock connect
        conn = sock.connect(server_address)
    except:
        return "error on sock 'connect' command with description: " + "'" + conn + "'"

    try:# sock send msg
        s = sock.sendall(msg.encode())
    except:
        return "error on sock 'sendall' command with description: " + "'" + s + "'"

    if s == None:
        try:
            data = sock.recv(1024)
        except:
            return data

        if data.decode() == msg:
            sock.close()
            return 'ok'
        else:
            sock.close()
            return 'error on received echo msg'
    else:
        sock.close()
        return 'error on sending msg to server'
