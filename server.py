#!usr/bin/python
import time
import json
import socket
import select
import random
import threading

serversock = None
HOST = '0.0.0.0'
PORT = 6546
SOCKET_TIMEOUT = 5

all_players = {}
board = None

class Player:
	def __init__(self, socket, name = 'anonymous'):
		self.name = name
		self.score = 0
		self.hand = []
		self.socket = socket
		self.card = None

	def set_hand(self, hand):
		self.hand = hand
		self.socket.send(bytes(json.dumps(hand), 'utf-8'))

	def set_card(self, card):
		self.card = card

	def __del__(self):
		self.socket.close()

class Board:
	def __init__(self, rows):
		self.rows = [[i] for i in rows]

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
					# broadcast(list(all_players.keys()), data)
					is_start = data == b'start\n' or data == b'start\r\n'
					is_give_card = chr(data[0]) == 'g'

					if is_start:
						cards = list(range(1, 25))
						random.shuffle(cards)

						for player in all_players.values():
							player.set_hand(cards[:10])
							cards = cards[10:]

						board = Board(cards[:4])
						data = bytes(json.dumps(board.rows), 'utf-8')
						broadcast(list(all_players.keys()), data)
					elif is_give_card:
						current_cards = int(data[1:])

						all_players[client].set_card(current_cards)

						current_cards = [p.card for p in all_players.values() if p.card]

						if len(current_cards) == len(all_players):
							broadcast(list(all_players.keys()), b'megvagyunk')
					else:
						print('unknown')

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
