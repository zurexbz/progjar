import sys
import socket
import logging
from concurrent.futures import ThreadPoolExecutor

def send_data():
    # Create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.warning("open socket")

    server_address = ('172.18.0.5', 45000)
    logging.warning(f"opening socket {server_address}")
    sock.connect(server_address)

    request = 'TIME \r\n'

    try:
        logging.warning(f"opening socket {server_address}")
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
    with ThreadPoolExecutor() as executor:
        while True:
            executor.submit(send_data)
            thread += 1
            print(f"Thread amount: {thread}")
