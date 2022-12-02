#!usr/bin/python
import enum
import json

import board
import server_socket
from player import Player

class MESSAGE_TYPE(enum.Enum):
	CONTROL = 0
	INFO = 1
	QUERY = 2
	ERROR = 3

class Game:
	def __init__(self, serversocket, score_limit = 66, nturn = 10):
		self.players = {}
		self.board = None
		self.ssock = serversocket
		self.turn = 0
		self.score_limit = score_limit
		self.cards_dealt = nturn

	def run(self):
		print('game: running')
		for client, msg, op in self.ssock.listen():
			print(msg, op)
			self.process_data(client, msg, op)
			if self.turn == self.cards_dealt:
				print('This round ended!')
				self.print_scoreboard()
				break
		#print('Game ended!')
		#print('Final scores:')
		#self.print_scoreboard()

	def print_scoreboard(self):
		for i, p in enumerate(sorted(self.players.values(), key=lambda p: p.score)):
			print(i + 1, ':', p.name, '-', p.score)

	def process_data(self, client, data_in_bytes, playerOperation):
		if playerOperation == server_socket.SOCKET_OP.NEW_CONNECTION:
			self.handle_new_connection(client)
		elif playerOperation == server_socket.SOCKET_OP.HANGUP:
			self.handle_disconnect(client)
		elif playerOperation == server_socket.SOCKET_OP.DATA_IN:
			self.process_message(client, data_in_bytes)
		else:
			print('process_data: unknown operation:', playerOperation)
			exit(1)

	def handle_new_connection(self, client):
		self.players[client] = Player(client)

	def handle_disconnect(self, client):
		del self.players[client]

	def process_message(self, client, bmsg):
		msg = str(bmsg, 'utf-8').strip()

		#TODO: refactor
		is_start = msg[0] == 's'
		is_give_card = msg[0] == 'g'
		is_choice = msg[0] in "cr"

		if is_start:
			self.start()
		elif is_give_card:
			try:
				current_cards = int(msg[1:])
			except:
				return
			self.giveCard(client, current_cards)
		elif is_choice:
			self.choice()
		else:
			print('unknown:', msg)

	def is_valid_msg(self, msg):
		try:
			res = json.loads(msg)
			print('type', res.get('type'))
			return True
		except(json.decoder.JSONDecodeError):
			print('json decode error...')
			return False

	def start(self):
		self.board = board.Board()

		for player in self.players.values():
			player.set_hand(self.board.draw(self.cards_dealt))

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
		for p in players_ready:
			p.hand.remove(p.card)
			p.card = None
		self.turn = self.turn + 1
		self.broadcast_turn()

	def broadcast_turn(self):
		board = dict()
		board['board'] = self.board.rows
		for p in self.players.values():
			msg = board.copy()
			msg['hand'] = p.hand
			self.ssock.broadcast([p.socket], json.dumps(msg))
