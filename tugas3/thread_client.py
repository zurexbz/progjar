import sys
import socket
import logging
import threading

class send_data(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Create TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.warning("open socket")

        server_address = ('172.18.0.5', 45000)
        logging.warning(f"opening socket {server_address}")
        sock.connect(server_address)

        try:
            request = 'TIME \r\n'
            logging.warning(f"Client request server for {request}")
            sock.sendall(request.encode())
            while True:
                data = sock.recv(16)
                logging.warning(f"Time from Server: {data}")
        finally:
            logging.warning("closing")
            sock.close()
        return


if __name__=='__main__':
    thread_count = 0
    while True:
        thread = send_data()
        thread.daemon = True
        thread.start()
        thread_count += 1
        print(f"Thread amount: {thread_count}")
