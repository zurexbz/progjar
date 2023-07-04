import threading
import socket
import json
import logging
import sys
from chat import Chat

chatserver = Chat()


class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        rcv = ""
        while True:
            data = self.connection.recv(32)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv[-2:] == '\r\n':
                    logging.warning('data dari client: {}'.format(rcv))
                    hasil = json.dumps(chatserver.proses(rcv))
                    hasil = hasil + '\r\n\r\n'
                    logging.warning('balas ke client: {}'.format(hasil))
                    self.connection.sendall(hasil.encode())
                    rcv = ""
            else:
                break

        self.connection.close()


class Server(threading.Thread):
    def __init__(self, portnumber):
        self.portnumber = portnumber
        self.clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.portnumber))
        logging.warning('Server berjalan di port {}'.format(self.portnumber))
        self.my_socket.listen(1)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning('Koneksi dari {}'.format(self.client_address))
            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.clients.append(clt)


def main():
    portnumber = 8999
    for arg in sys.argv:
        if sys.argv.index(arg) == 0:
            continue

        try:
            portnumber = int(arg)
            svr = Server(portnumber)
            svr.start()
        except:
            break


if __name__ == '__main__':
    main()
