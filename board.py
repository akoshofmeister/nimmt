import enum
import random

class CANDIDATE(enum.Enum):
	TOO_LOW = 0
	PENALTY = 1
	PUT = 2

class Board:
	PENALTIES = [(55, 7), (11, 5), (10, 3), (5, 2)]

	def __init__(self, nrows = 4, deck_size = 104, max_row_len = 5):
		self.ncards = deck_size
		self.deck = list(range(1, deck_size + 1))
		random.shuffle(self.deck)
		#print(self.deck)
		self.rows = [[c] for c in self.draw(nrows)]
		#print(self.rows)
		self.max_row_len = max_row_len

	@classmethod
	def card_value(cls, card):
		for divider, penalty in Board.PENALTIES:
			if (card % divider) == 0:
				return penalty
		return 1

	@classmethod
	def calc_penalty(cls, row):
		return sum(map(Board.card_value, row))

	def draw(self, n = 1):
		print(len(self.deck), n)
		assert len(self.deck) >= n, 'draw: not that many cards in the deck'
		top_n = self.deck[:n]
		self.deck = self.deck[n:]
		return top_n

	def reset_row(self, row_ind, card):
		assert 0 <= row_ind < len(self.rows), 'reset_row: index is out of the range'
		assert 0 < card <= self.ncards, 'reset_row: invalid card'
		penalty = self.calc_penalty(self.rows[row_ind])
		self.rows[row_ind] = [card]
		return penalty

	def place_card(self, card):
		mindiff = self.ncards
		candidate_row = None
		minind = -1
		for i, row in enumerate(self.rows):
			diff = card - row[-1]
			if 0 < diff < mindiff:
				mindiff = diff
				minind = i
				candidate_row = row
		if not candidate_row:
			return (CANDIDATE.TOO_LOW, None) #TODO
		elif len(candidate_row) == self.max_row_len:
			penalty = self.calc_penalty(candidate_row)
			self.rows[minind] = [card]
			print(self.rows)
			return (CANDIDATE.PENALTY, penalty)
		else:
			candidate_row.append(card)
			return (CANDIDATE.PUT, None) #TODO
