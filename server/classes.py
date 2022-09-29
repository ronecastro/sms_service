import socket, pickle

class socketServer:
    def __init__(self, address, debug=False):
        self.address = address #(ip, port)
        self.debug = debug

    def create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock
        except Exception as e:
            return e

    def bind_address(self, sock):
        try:
            sock.bind(self.address)
            return 'ok'
        except Exception as e:
            return e

    def listen(self, sock):
        try:
            sock.listen()
            return 'ok'
        except Exception as e:
            return e

    def accept_connection(self, sock):
        conn, addr = sock.accept()
        return conn, addr

    def send_data(self, conn, data):
        try:
            conn.sendall(pickle.dump(data))
            return 'ok'
        except Exception as e:
            return 'error on send_data', e

    def receive_data(self, conn, size, echo=False):
        try:
            data = conn.recv(size)
            if echo:
                conn.sendall(data) # echo
            return pickle.loads(data)
        except Exception as e:
            return 'error on receive_data', e
    
    def close(self, sock):
        sock.close()

# ip='localhost'
# port=5007
# address = (ip, port)
# sv = Server(address)