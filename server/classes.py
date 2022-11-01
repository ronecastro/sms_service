import socket, pickle
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
from time import sleep
from multiprocessing import Value
from miscfunctions import current_path

class socketServer:
    def __init__(self, address, debug=False):
        self.address = address #(ip, port)
        self.debug = debug

    def create_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return 'ok'
        except Exception as e:
            return e

    def bind_address(self):
        try:
            self.sock.bind(self.address)
            return 'ok'
        except Exception as e:
            return e

    def listen(self):
        try:
            self.sock.listen()
            return 'ok'
        except Exception as e:
            return e

    def accept_connection(self):
        conn, addr = self.sock.accept()
        return conn, addr

    def connect(self, addr):
        try:
            self.connect(addr)
            return 'ok'
        except Exception as e:
            return e

    def send_data(self, data):
        try:
            self.sock.sendall(pickle.dump(data))
            return 'ok'
        except Exception as e:
            return 'error on send_data', e

    def receive_data(self, sock, size=1024, echo=False):
        try:
            data = sock.recv(size)
            if echo:
                sock.sendall(data) # echo
            return pickle.loads(data)
        except Exception as e:
            return 'error on receive_data', e
    
    def close(self):
        self.sock.close()

class sysIcon:
    def __init__(self, exit, debug=False):
        self.exit = exit
        self.debug = debug
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.icon = QIcon(current_path("message.png"))
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        self.menu = QMenu()
        self.quit = QAction("Quit")
        self.quit.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit)
        self.tray.setContextMenu(self.menu)

    def run(self):
        self.app.exec_()
        self.exit.value = True
        # return self.exit.value

# icon = sysIcon(False)
# print(icon.run())

# ip='localhost'
# port=5007
# address = (ip, port)
# sv = Server(address)