#!usr/bin/python
import time
import socket
import select
import threading

serversock = None
HOST = '0.0.0.0'
PORT = 6546
SOCKET_TIMEOUT = 5

all_connections = list()

def broadcast(client_list, data):
	for c in client_list:
		c.send(data)

def listen(host, port):
	serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serversock.bind((host, port))
	serversock.listen(10)
	while True:
		print('waiting in select')
		all_socks = all_connections + [serversock]
		readable, writable, exceptional = select.select(
				all_socks, [], all_socks)
		if len(exceptional) >= 1:
			print('exceptional! %s' % (client_address,))
			continue
		if len(readable) >= 1:
			print('len >= 1')
			if serversock in readable:
				print('serversock in')
				current_connection, client_address = serversock.accept()
				all_connections.append(current_connection)
				print('%s connected' % (client_address,))
			else:
				print('broadcast')
				client = readable[0]
				data = client.recv(1024)
				if len(data) <= 0:
					print('client - hangup')
					all_connections.remove(client)
					client.shutdown(socket.SHUT_RDWR)
					client.close()
				else:
					broadcast(all_connections, data)
			continue

if __name__ == '__main__':
	try:
		listen(HOST, PORT)
	except KeyboardInterrupt:
		print('interrupt - exiting')
		print('n_connections: %d' % (len(all_connections),))
		for client in all_connections:
			client.shutdown(socket.SHUT_RDWR)
			client.close()
		time.sleep(1)
		exit(9)
