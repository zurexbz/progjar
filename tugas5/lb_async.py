import socket
import time
import sys
import asyncore
import logging


class BackendList:
    def __init__(self):
        self.servers = []
        self.servers.append(('127.0.0.1', 8001))
        self.servers.append(('127.0.0.1', 8002))
        self.servers.append(('127.0.0.1', 8003))
        self.servers.append(('127.0.0.1', 8004))
        self.current = 0

    def getserver(self):
        s = self.servers[self.current]
        self.current = self.current + 1
        if self.current >= len(self.servers):
            self.current = 0
        return s


class Backend(asyncore.dispatcher_with_send):
    def __init__(self, targetaddress):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(targetaddress)
        self.client_socket = None

    def handle_read(self):
        if self.client_socket:
            try:
                data = self.recv(8192)
                if data:
                    self.client_socket.send(data)
            except Exception as e:
                logging.warning("Backend handle_read error: {}".format(e))
                self.close()
    
    def handle_close(self):
        try:
            self.close()
            if self.client_socket:
                self.client_socket.close()
        except Exception as e:
            logging.warning("Backend handle_close error: {}".format(e))


class ProcessTheClient(asyncore.dispatcher):
    def __init__(self, sock, backend):
        asyncore.dispatcher.__init__(self, sock)
        self.backend = backend
        self.backend.client_socket = self

    def handle_read(self):
        try:
            data = self.recv(8192)
            if data:
                self.backend.send(data)
        except Exception as e:
            logging.warning("ProcessTheClient handle_read error: {}".format(e))
            self.close()

    def handle_close(self):
        self.close()
        if self.backend:
            self.backend.close()


class Server(asyncore.dispatcher):
    def __init__(self, portnumber):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', portnumber))
        self.listen(5)
        self.bservers = BackendList()
        logging.warning("load balancer running on port {}".format(portnumber))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logging.warning("connection from {}".format(repr(addr)))

            bs = self.bservers.getserver()
            logging.warning("koneksi dari {} diteruskan ke {}".format(addr, bs))
            backend = Backend(bs)

            handler = ProcessTheClient(sock, backend)


def main():
    portnumber = 55555
    try:
        portnumber = int(sys.argv[1])
    except:
        pass
    svr = Server(portnumber)
    asyncore.loop()


if __name__ == "__main__":
    main()
