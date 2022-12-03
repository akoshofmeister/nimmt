#!usr/bin/python
import enum
import json

import board
import server_socket
from player import Player

class CONTROL_MSG_TYPE(enum.Enum):
	ERROR = -1
	UNKNOWN = 0
	START = 1

class Game:
	def __init__(self, serversocket, score_limit = 66, nturn = 10):
		self.players = {}
		self.board = None
		self.ssock = serversocket
		self.turn = 1
		self.score_limit = score_limit
		self.cards_dealt = nturn

	def get_controll_message_action(self, msg): #TODO: classmethod
		try:
			print('json:', msg)
			res = json.loads(msg)
			action = res.get('action')
			print('action:', action)
			if action == 'start':
				return CONTROL_MSG_TYPE.START
			return CONTROL_MSG_TYPE.UNKNOWN
		except(json.decoder.JSONDecodeError):
			print('json decode error...')
			return CONTROL_MSG_TYPE.ERROR

	def run(self):
		print('game: running')
		print('waiting to start...')
		for client, msg, op in self.ssock.listen():
			if op == server_socket.SOCKET_OP.DATA_IN:
				action = self.get_controll_message_action(msg)
				if action == CONTROL_MSG_TYPE.START:
					break
			else:
				self.process_connections(client, msg, op)
		self.new_game()
		self.broadcast_turn()
		for client, msg, op in self.ssock.listen():
			if op != server_socket.SOCKET_OP.DATA_IN:
				print('Unexpected socket messages!')
				continue
			self.process_message(client, msg)
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

	def process_connections(self, client, data_in_bytes, playerOperation):
		if playerOperation == server_socket.SOCKET_OP.NEW_CONNECTION:
			self.handle_new_connection(client)
		elif playerOperation == server_socket.SOCKET_OP.HANGUP:
			self.handle_disconnect(client)
		#elif playerOperation == server_socket.SOCKET_OP.DATA_IN:
		#	return
		else:
			print('process_connections: unknown operation:', playerOperation)
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

		if is_start:
			self.start()
			self.broadcast_game_format()
			self.broadcast_turn()
		elif is_give_card:
			try:
				current_cards = int(msg[1:])
			except:
				return
			self.giveCard(client, current_cards)
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

	def new_game(self):
		self.board = board.Board()
		for player in self.players.values():
			player.set_hand(self.board.draw(self.cards_dealt))

	def giveCard(self, client, card):
		if not self.players[client].set_card(card):
			send_json = json.dumps({'type' : 'error', 'Not in your hand' : str(card)})
			self.ssock.broadcast([client], send_json) # TODO: broadcast?
			return
		players_ready = [p for p in self.players.values() if p.card]
		if len(players_ready) != len(self.players):
			return
		self.place_all_cards()

	def place_all_cards(self):
		players_ready = sorted(self.players.values(), key=lambda p: p.card)
		for p in players_ready:
			ret, arg = self.board.place_card(p.card)
			if ret == board.CANDIDATE.TOO_LOW:
				selection = p.select_row(self.board.rows)
				penalty = self.board.reset_row(selection, p.card)
				p.score = p.score + penalty
				#print(p.name, p.card, 'low: ', p.score)
			elif ret == board.CANDIDATE.PENALTY:
				p.score = p.score + arg
				#print(p.name, p.card, 'penalty:', p.score)
			elif ret == board.CANDIDATE.PUT:
				#print(p.name, p.card, 'ok')
				pass
			else:
				print('place_cards: unknown operation:', ret)
				exit(1)
		#print(self.board.rows)
		for p in players_ready:
			p.hand.remove(p.card) # TODO: move to player.py
			p.card = None
		self.turn = self.turn + 1
		self.broadcast_turn()

	def broadcast_game_format(self):
		msg = {
			'type' : 'info',
			'score_limit' : self.score_limit,
			'nturns' : self.cards_dealt,
			'nrows' : len(self.board.rows),
			'row_len' : self.board.max_row_len,
			'nplayers' : len(self.players) }
		self.ssock.broadcast(self.players.keys(), json.dumps(msg))

	def broadcast_turn(self):
		board = { 'type' : 'query', 'action' : 'give_card', 'board' : self.board.rows }
		for p in self.players.values():
			msg = board.copy()
			msg['hand'] = p.hand
			msg['turn'] = self.turn
			self.ssock.broadcast([p.socket], json.dumps(msg))
