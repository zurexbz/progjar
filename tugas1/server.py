import sys
import socket
import logging

logging.basicConfig(level=logging.INFO)

try:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 32)

    # Bind the socket to the port
    server_address = ('0.0.0.0', 32444) #--> gunakan 0.0.0.0 agar binding ke seluruh ip yang tersedia

    logging.info(f"starting up on {server_address}")
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)
    #1 = backlog, merupakan jumlah dari koneksi yang belum teraccept/dilayani yang bisa ditampung, diluar jumlah
    #             tsb, koneks akan direfuse
    while True:
        # Wait for a connection
        logging.info("waiting for a connection")
       	connection, client_address = sock.accept()
       	logging.info(f"connection from {client_address}")
        # Receive the data in small chunks and retransmit it
        filename = 'tugas1.txt'
        f = open(filename, 'rb')
        l = f.read(32)
        while l:
            connection.sendall(l)
            l = f.read(32)
        # Clean up the connection
	
        connection.close()
except Exception as ee:
    logging.log(logging.INFO, f"ERROR: {str(ee)}")
finally:
    logging.log(logging.INFO, "closing")
    sock.close()
