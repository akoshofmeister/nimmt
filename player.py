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

    def __del__(self):
        self.socket.close()