import sys
import socket
import logging
from multiprocessing import Process

def send_data():
    # Create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.warning("open socket")

    server_address = ('172.18.0.3', 45000)
    logging.warning(f"opening socket {server_address}")
    sock.connect(server_address)

    request = 'TIME \r\n'

    try:
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
    thread = 0
    for i in range(0, 2000):
        thread += 1
        process = Process(target=send_data)
        process.start()
        print(f"Process amount: {thread}")
