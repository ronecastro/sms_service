import json, socket, pickle
class notification_class:
    def __init__(self, id, user_id, notification, last_sent):
        self.id = id
        self.user_id = user_id
        self.notification = notification
        self.last_sent = last_sent
    
    def json(self):
        n = json.loads(self.notification)
        return n

class user_class:
    def __init__(self, id, username, email, phone):
        self.id = id
        self.username = username
        self.email = email
        self.phone = phone

class empty_class:
    pass

class socketClient:
    def __init__(self, address, debug=False):
        self.address = address
        self.debug = debug

    def create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            return sock
        except Exception as e:
            return 'error on create_socket', e

    def connect(self, sock):
        try:
            sock.connect(self.address)
            return 'ok'
        except Exception as e:
            return e

    def send_data(self, sock, data):
        try:
            sock.sendall(pickle.dumps(data))
            return 'ok'
        except Exception as e:
            return 'error on send_data', e

    def receive_data(self, sock, size, echo=False):
        try:
            data = sock.recv(size)
            if echo:
                sock.sendall(data) # echo
            return pickle.loads(data)
        except Exception as e:
            return 'error on receive_data', e

    def close(self, sock):
        sock.close()