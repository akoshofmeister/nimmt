import json

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
		if card in self.hand:
			self.card = card
			return self.card
		return None

	def query_user(self, msg, options):
		num = None
		bmsg = bytes(msg + str(options), 'utf-8')
		while True:
			self.socket.send(bmsg)
			num = int(self.socket.recv(1024).strip())
			if num in options:
				break
		return num

	def select_row(self, nrows):
		return self.query_user('Pick up a row!', list(range(nrows)))

	def __del__(self):
		self.socket.close()
