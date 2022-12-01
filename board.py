import enum

class CANDIDATE(enum.Enum):
	TOO_LOW = 0
	PENALTY = 1
	PUT = 2

class Board:
	ALL_CARDS_COUNT = 104
	PENALTIES = zip([55, 11, 10, 5], [7, 5, 3, 2])

	def __init__(self, rows):
		self.rows = [[i] for i in rows]

	@classmethod
	def card_value(cls, card):
		for divider, penalty in Board.PENALTIES:
			if card % divider == 0:
				return penalty
		return 1

	@classmethod
	def calc_penality(cls, row):
		return sum(map(Board.card_value, row))

	def reset_row(self, row_ind, card):
		self.rows[row_ind] = [card]

	def place_card(self, card):
		mindiff = Board.ALL_CARDS_COUNT
		candidate = None
		for row in self.rows:
			diff = card - row[-1]
			if diff > 0 and diff < mindiff:
				mindiff = diff
				candidate = row
		if not candidate:
			print(self.rows)
			return CANDIDATE.TOO_LOW
		elif len(candidate) == 5:
			return CANDIDATE.PENALTY
		else:
			candidate.append(card)
			print(self.rows)
			return CANDIDATE.PUT

	def place_all_cards(self, cards):
		cards.sort()
		choosed = []
		for card in cards:
			choosed.append((card, self.place_card(card)))
		return choosed
