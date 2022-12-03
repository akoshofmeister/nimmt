#!usr/bin/python
import enum
import json

import board
import server_socket
from player import Player


class MSG_TYPE(enum.Enum):
	ERROR = -1
	UNKNOWN = 0
	START = 1
	QUIT = 2
	GIVE_CARD = 3

class GAME_STATE(enum.Enum):
	LOBBY = 0
	QUIT = 1
	PLAY = 2

class Game:
	def __init__(self, serversocket, score_limit=66, nturn=10):
		self.players = {}
		self.board = None
		self.ssock = serversocket
		self.turn = 1
		self.score_limit = score_limit
		self.cards_dealt = nturn
		self.game_state = GAME_STATE.LOBBY

	def get_controll_message_action(self, msg):  # TODO: classmethod
		try:
			print('json:', msg)
			res = json.loads(msg)
			action = res.get('action')
			print('action:', action)
			if action == 'start':
				return MSG_TYPE.START
			elif action == 'quit':
				return MSG_TYPE.QUIT
			return MSG_TYPE.UNKNOWN
		except(json.decoder.JSONDecodeError):
			print('json decode error...')
			return MSG_TYPE.ERROR

	def run(self):
		print('game: running')
		print('waiting to start...')

		while self.game_state != GAME_STATE.QUIT:
			if self.game_state == GAME_STATE.LOBBY:
				self.lobby()
			else:
				self.game()

	def lobby(self):
		for client, msg, op in self.ssock.listen():
			if op == server_socket.SOCKET_OP.DATA_IN:
				action = self.get_controll_message_action(msg)
				if action == MSG_TYPE.START:
					self.game_state = GAME_STATE.PLAY
					break
				elif action == MSG_TYPE.QUIT:
					self.game_state = GAME_STATE.QUIT
					break
			else:
				self.process_connections(client, msg, op)

	def game(self):
		self.new_game()
		while self.turn <= self.cards_dealt:
			self.broadcast_turn()
			self.play_turn()

		self.game_state = GAME_STATE.LOBBY
		self.print_scoreboard()

	def play_turn(self):
		for client, msg, op in self.ssock.listen():
			if op != server_socket.SOCKET_OP.DATA_IN:
				print('Unexpected socket messages!')
				continue
			self.process_message(client, msg)

	def print_scoreboard(self):
		for i, p in enumerate(sorted(self.players.values(), key=lambda p: p.score)):
			print(i + 1, ':', p.name, '-', p.score)

	def process_connections(self, client, data_in_bytes, playerOperation):
		if playerOperation == server_socket.SOCKET_OP.NEW_CONNECTION:
			self.handle_new_connection(client)
		elif playerOperation == server_socket.SOCKET_OP.HANGUP:
			self.handle_disconnect(client)
		# elif playerOperation == server_socket.SOCKET_OP.DATA_IN:
		#	return
		else:
			print('process_connections: unknown operation:', playerOperation)
			exit(1)

	def handle_new_connection(self, client):
		self.players[client] = Player(client)

	def handle_disconnect(self, client):
		del self.players[client]

	def process_message(self, client, bmsg):
		msg_type, payload = self.parse_message(bmsg)

		if msg_type == MSG_TYPE.GIVE_CARD:
			try:
				current_cards = int(payload)
			except:
				print('error parsing GIVE_CARD', payload)
				return
			self.get_card(client, current_cards)
		else:
			print('unknown command')

	def parse_message(self, bmsg):
		try:
			msg = json.loads(str(bmsg, 'utf-8').strip())

			if msg.get('action') == 'give_card':
				return MSG_TYPE.GIVE_CARD, msg.get('card')

			return MSG_TYPE.ERROR, None
		except json.decoder.JSONDecodeError:
			print('json decode error...')
			return MSG_TYPE.ERROR, None

	def new_game(self):
		self.board = board.Board()
		for player in self.players.values():
			player.set_hand(self.board.draw(self.cards_dealt))

	def get_card(self, client, card):
		if not self.players[client].set_card(card):
			send_json = json.dumps({'type': 'error', 'Not in your hand': str(card)})
			self.ssock.broadcast([client], send_json)  # TODO: broadcast?
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
			# print(p.name, p.card, 'low: ', p.score)
			elif ret == board.CANDIDATE.PENALTY:
				p.score = p.score + arg
			# print(p.name, p.card, 'penalty:', p.score)
			elif ret == board.CANDIDATE.PUT:
				# print(p.name, p.card, 'ok')
				pass
			else:
				print('place_cards: unknown operation:', ret)
				exit(1)
		# print(self.board.rows)
		for p in players_ready:
			p.hand.remove(p.card)  # TODO: move to player.py
			p.card = None
		self.turn = self.turn + 1
		self.broadcast_turn()

	def broadcast_game_format(self):
		msg = {
			'type': 'info',
			'score_limit': self.score_limit,
			'nturns': self.cards_dealt,
			'nrows': len(self.board.rows),
			'row_len': self.board.max_row_len,
			'nplayers': len(self.players)}
		self.ssock.broadcast(self.players.keys(), json.dumps(msg))

	def broadcast_turn(self):
		board = {'type': 'query', 'action': 'give_card', 'board': self.board.rows}
		for p in self.players.values():
			msg = board.copy()
			msg['hand'] = p.hand
			msg['turn'] = self.turn
			self.ssock.broadcast([p.socket], json.dumps(msg))
