from iofunctions import fromcfg, socketServer as sockserver
from multiprocessing import Process, Queue
from time import sleep
import json, psutil

def on_new_client(connection, client_address, queue):
    while True:
        try:
            #print('connection from', client_address)
            ip1 = fromcfg("IP", "client_ip1")
            ip2 = fromcfg("IP", "client_ip2")
            ip3 = fromcfg("IP", "client_ip3")
            ip4 = fromcfg("IP", "client_ip4")
            data = ''
            if (client_address[0] == ip1 or 
                client_address[0] == ip2 or 
                client_address[0] == ip3 or 
                client_address[0] == ip4):
                data = sockserver.receive_data(connection, 1024, echo=True)
                if not 'error' in data:
                    queue.put_nowait(data) #increment queue
                else:
                    return 'error: ', data
            else:
                connection.close()
        finally:
            #Clean up the connection
            connection.close()
            break
    #print('on_new_client OFF')
    quit()

def init():
    # Create a TCP/IP socket
    sock = sockserver.create_socket()
    sockserver.bind_address(sock)

    # Bind the socket to the port
    ip = str(fromcfg("ADDRESS", "ip"))
    port = int(fromcfg("ADDRESS", "port"))
    #print(ip, port)
    if 'error' in (ip or port):
        exit()
    else:
        server_address = (ip, port)
        sockserver.bind_address(server_address)
        sockserver.listen()
        return sockserver

def server(sock, queue, stop):
    data = ''
    while True:
        if stop.value:
            exit()
        sleep(1)
        connection, client_address = sock.accept()
        try:
            p = Process(target=on_new_client, args=(connection, client_address, queue))
            p.start()
        finally:
            sleep(1)

def watcherseye(queue, stop):
    while True:
        if stop.value:
            exit()
        sleep(1)
        if queue.empty() == False:
            n = queue.get_nowait()
            print(n)

def main():
    plist = []
    for p in psutil.process_iter():
        try:
            plist.append(p.name())
        except psutil.AccessDenied:
            pass
    print(plist)

main()