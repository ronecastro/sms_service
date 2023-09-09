from iofunctions import fromcfg, socketServer
from multiprocessing import Process, Queue, Value
from time import sleep
from ctypes import c_bool
from os import _exit
from classes import sysIcon
from modem_usb import Modem
import psutil, setproctitle, subprocess, signal

gsock = None
gexit = Value(c_bool, False)

# This function receives the message sent from client
def on_new_client(sock, connection, client_address, queue):
    setproctitle.setproctitle('notificationserver-spawn')
    while True:
        try:
            # print('on_new_client running')
            ip1 = fromcfg("IP", "client_ip1")
            ip2 = fromcfg("IP", "client_ip2")
            ip3 = fromcfg("IP", "client_ip3")
            ip4 = fromcfg("IP", "client_ip4")
            data = ''
            if (client_address[0] == ip1 or
                client_address[0] == ip2 or
                client_address[0] == ip3 or
                client_address[0] == ip4):
                data = sock.receive_data(connection, echo=True)
                # print('data', data)
                if not 'error' in data:
                    queue.put(data) #increment queue
                    sleep(1)
                else:
                    return 'error: ', data
            else:
                sock.close()
        except Exception as e:
            return 'error on_new_client', e
        finally:
            sock.close()
            break
    _exit(0)

def init():
    ip = str(fromcfg("SERVER", "ip"))
    port = int(fromcfg("SERVER", "port"))
    if 'error' in (ip or port):
        raise Exception('error on ip or port')
    server_address = (ip, port)
    sock = socketServer(server_address)
    if (sock.create_socket()) == 'ok':
        sock.bind_address()
        sock.listen()
    return sock

def server(sock, queue, exit):
    setproctitle.setproctitle('notificationserver')
    # print('server initialized')
    while True:
        if exit.value:
            break
        else:
            # print('connection started')
            connection, client_address = sock.accept_connection()
            # print('connection accepted')
            try:
                p = Process(name='notificationserver-spawn', target=on_new_client, \
                    args=(sock, connection, client_address, queue))
                p.start()
            except Exception as e:
                print('error on spanw', e)
                return e
            finally:
                init()
    print('exit server')
    _exit(0)


def watcherseye(queue, exit):
    setproctitle.setproctitle('watcherseye')
    # print('watcherseye initialized')
    while True:
        if exit.value:
            # print('exit watcherseye')
            _exit(0)
        else:
            sleep(2)
            if queue.empty() == False:
                data = queue.get_nowait()
                print('watcherseye queue:', data)
                owner = data[0][0]
                phone = data[0][1]
                email = data[0][2]
                msg = data[1]
                print('owner', owner)
                print('phone', phone)
                print('email', email)
                print('msg', msg)
                # m = Modem()
                # m.initialize()
                # m.sendsms(number=phone, msg=msg)
                # m.closeconnection()

def search(list, pname):
    pnum = 0
    for i in range(len(list)):
        if list[i] == pname:
            pnum += 1
    if pnum > 1:
        return True
    return False

def icon(exit):
    icon = sysIcon(exit)
    icon.run()

def handler(signum, frame):
    ip = str(fromcfg("ADDRESS", "ip"))
    port = int(fromcfg("ADDRESS", "port"))
    if 'error' in (ip or port):
        raise Exception('error on ip or port')
    exit.value = True
    sleep(1)
    addr = (ip, port)
    ans = gsock.connect(addr)
    # print('handler ans', ans)
    sleep(1)
    _exit(0)

def main():
    setproctitle.setproctitle('NotificationServiceServer')
    proc = 'NotificationServiceServer'
    plist = []
    global gexit
    # gexit = Value(c_bool, False)
    signal.signal(signal.SIGINT, handler)
    for p in psutil.process_iter():
        try:
            plist.append(p.name())
        except psutil.AccessDenied:
            pass
    if search(plist, proc):
        subprocess.run(["/usr/bin/notify-send", "-i", "process-stop", \
            "Notification Service Server", \
            "Another instance is already running!"])
        print('already running')
        _exit(126) # Cannot Execute: 126
    try:
        # pass
        global gsock
        gsock = init()
    except Exception as e:
        return 'error on starting the socket', e
    q = Queue()
    # p* = Process(name=proc, target=icon, args=(gexit,))
    # p*.start()
    p1 = Process(name='notificationserver', target=server, args=(gsock, q, gexit,))
    p1.start()
    p2 = Process(name='watcherseye', target=watcherseye, args=(q, gexit,))
    p2.start()
    while True:
        # print('exit main')
        sleep(1)
        if gexit.value:
            _exit(0)

# main()

main()
# sock = init()
# conn, addr = sock.accept_connection()
# data = sock.receive_data(conn, echo=True)
# sock.close()
# print(data)
