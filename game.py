#!usr/bin/python
import json

import board
import server_socket
from player import Player

class Game:
	def __init__(self, serversocket):
		self.players = {}
		self.board = None
		self.ssock = serversocket

	def run(self):
		print('game: running')
		for client, msg, op in self.ssock.listen():
			print(client, msg, op)
			self.process_data(client, msg, op)

	def process_data(self, client, data_in_bytes, playerOperation):
		if playerOperation == server_socket.SOCKET_OP.NEW_CONNECTION:
			self.players[client] = Player(client)
			return
		elif playerOperation == server_socket.SOCKET_OP.HANGUP:
			del self.players[client]
			return
		elif playerOperation == server_socket.SOCKET_OP.DATA_IN:
			pass
		else:
			print('process_data: unknown operation:', playerOperation)
			exit(1)

		data = str(data_in_bytes, 'utf-8').strip()

		#TODO: refactor
		is_start = data[0] == 's'
		is_give_card = data[0] == 'g'
		is_choice = data[0] in "cr"

		if is_start:
			self.start()
		elif is_give_card:
			try:
				current_cards = int(data[1:])
			except:
				return
			self.giveCard(client, current_cards)
		elif is_choice:
			self.choice()
		else:
			print('unknown:', data)

	def start(self):
		self.board = board.Board(4, 104, 5) #TODO: def parameters

		for player in self.players.values():
			player.set_hand(self.board.draw(10))

		data = json.dumps(self.board.rows)
		self.ssock.broadcast(list(self.players.keys()), data)

	def giveCard(self, client, card):
		if not self.players[client].set_card(card):
			send_json = '{"Not in your hand":' + str(card) + '}' # TODO
			self.ssock.broadcast([client], send_json) # TODO: broadcast?
			return
		players_ready = [p for p in self.players.values() if p.card]
		if len(players_ready) != len(self.players):
			return
		self.place_all_cards()

	def player2card(self, card):
		for p in self.players:
			if card in p.hand:
				return p
		return None

	def place_all_cards(self):
		players_ready = sorted(self.players.values(), key=lambda p: p.card)
		for p in players_ready:
			ret, arg = self.board.place_card(p.card)
			if ret == board.CANDIDATE.TOO_LOW:
				selection = p.select_row(len(self.board.rows))
				penalty = self.board.reset_row(selection, p.card)
				p.score = p.score + penalty
				print(p.name, p.card, 'low: ', p.score)
			elif ret == board.CANDIDATE.PENALTY:
				p.score = p.score + arg
				print(p.name, p.card, 'penalty:', p.score)
			elif ret == board.CANDIDATE.PUT:
				print(p.name, p.card, 'ok')
				pass
			else:
				print('place_cards: unknown operation:', ret)
				exit(1)
		print(self.board.rows)
		self.ssock.broadcast(list(self.players.keys()), "megvagyunk\n")
		for p in players_ready:
			p.hand.remove(p.card)
			p.card = None

	def choice(self):
		pass
