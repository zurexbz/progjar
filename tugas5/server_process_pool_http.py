from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection,address):
		rcv=""
		while True:
			try:
				data = connection.recv(32)
				if data:
					d = data.decode()
					rcv=rcv+d
					if rcv[-2:]=='\r\n':
						logging.warning("data dari client: {}" . format(rcv))
						hasil = httpserver.proses(rcv)
						hasil=hasil+"\r\n\r\n".encode()
						logging.warning("balas ke  client: {}" . format(hasil))
						connection.sendall(hasil)
						rcv=""
						connection.close()
						return
				else:
					break
			except OSError as e:
				pass
		connection.close()
		return

def Server(portnumber=8889):
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	my_socket.bind(('0.0.0.0', portnumber))
	my_socket.listen(1)
	logging.warning("running on port {}" . format(portnumber))

	with ProcessPoolExecutor(20) as executor:
		while True:
				connection, client_address = my_socket.accept()
				p = executor.submit(ProcessTheClient, connection, client_address)
				the_clients.append(p)
				jumlah = ['x' for i in the_clients if i.running()==True]
				print(jumlah)

def main():
	portnumber=8000
	try:
		portnumber=int(sys.argv[1])
	except:
		pass
	svr = Server(portnumber)

if __name__=="__main__":
	main()
