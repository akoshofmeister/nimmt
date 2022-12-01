#!usr/bin/python
import random
import json

from board import Board
from player import Player
from server_socket import broadcast

class Game:
	def __init__(self,serversocket):
		self.all_players = {}
		self.board = None
		serversocket.set_process_function(self.process_data)
		serversocket.listen()

	def process_data(self,client, data_in_bytes, playerOperation):
		if playerOperation:
			self.modifyPlayerList(playerOperation, client)
			return
		data = str(data_in_bytes, 'utf-8').strip()

		# broadcast(list(all_players.keys()), data)
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
			self.giveCard(client,current_cards)
		elif is_choice:
			self.choice()
		else:
			print('unknown ' + data)

	def start(self):
		cards = list(range(1, Board.ALL_CARDS_COUNT))
		random.shuffle(cards)

		for player in self.all_players.values():
			player.set_hand(cards[:10])
			cards = cards[10:]

		self.board = Board(cards[:4])
		data = json.dumps(self.board.rows)
		broadcast(list(self.all_players.keys()), data)

	def giveCard(self,client,current_cards):
		if self.all_players[client].set_card(current_cards) == None:
			send_json='{"Not in your hand":' + str(current_cards) + '}'
			broadcast([client], send_json)
			return
		current_cards = [p.card for p in self.all_players.values() if p.card]
		if len(current_cards) == len(self.all_players):
			response_places = self.board.place_all_cards(current_cards)
			print(response_places)
			# TODO response_places
			broadcast(list(self.all_players.keys()), "megvagyunk")

	def modifyPlayerList(self,playerOperation, client):
		if "ACCEPT" == playerOperation:
			self.all_players[client] = Player(client)
		else:
			del self.all_players[client]

	def choice(self):
		pass
