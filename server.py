#!usr/bin/python
import time
import json
import socket
import select
import threading

serversock = None
HOST = '0.0.0.0'
PORT = 6546
SOCKET_TIMEOUT = 5

all_players = {}

class Player:
	def __init__(self, socket, name = 'anonymous'):
		self.name = name
		self.score = 0
		self.hand = []
		self.socket = socket

	def set_hand(self, hand):
		self.hand = hand
		self.socket.send(bytes(json.dumps(hand), 'utf-8'))

	def __del__(self):
		self.socket.close()

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
		#all_socks = all_connections + [serversock]
		all_socks = list(all_players.keys()) + [serversock]
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
				new_player = Player(current_connection)
				new_player.set_hand([1,2,420,69])
				all_players[current_connection] = new_player
				print('%s connected' % (client_address,))
			else:
				print('broadcast')
				client = readable[0]
				data = client.recv(1024)
				if len(data) <= 0:
					print('client - hangup')
					del all_players[client]
				else:
					broadcast(list(all_players.keys()), data)
			continue

if __name__ == '__main__':
	try:
		listen(HOST, PORT)
	except KeyboardInterrupt:
		print('interrupt - exiting')
		print('n_connections: %d' % (len(all_players),))
		for client in all_players:
			del client
		time.sleep(1)
		exit(9)
