import sys
import socket
import logging



def send_data():
    # Create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.warning("open socket")

    # Connect socket with port 45000
    server_address = ('172.18.0.4', 45000)
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
    for i in range(1,10):
        send_data()
