table = [[15, 40], [5, 20], [1, 2, 22, 33], [4]]
print(table)

def query_user(options):
	num = None
	while True:
		print('select one!')
		print(options)
		num = int(input())
		if num in options:
			break
	return num

def select_row():
	#print table
	return query_user(list(range(4)))

#def select_card():
#	return query_user(hand)

def reset_row(row_ind, card):
	table[row_ind] = [card]

def place_card(card):
	mindiff = 104
	candidate = None
	for row in table:
		diff = card - row[-1]
		if diff > 0 and diff < mindiff:
			mindiff = diff
			candidate = row
	if not candidate or len(candidate) == 5:
		return False
	elif len(candidate) == 5:
		return True
	else:
		candidate.append(card)
		return True

def place_all_cards(cards):
	cards.sort()
	for card in cards:
		if place_card(card):
			pass; #print('ok')
		else:
			print(card, ': select a row!')
			selection = select_row()
			reset_row(selection, card)

#TODO: how to generalize this? (hint: rules)
def card_value(card):
	if card == 55:
		return 7
	elif (card % 11) == 0:
		return 5
	elif (card % 10) == 0:
		return 3
	elif (card % 5) == 0:
		return 2
	else:
		return 1

def calc_penality(row):
	return sum(map(card_value, row))

place_all_cards([3, 10, 35, 34])
print(table)
table.sort(key=lambda x: x[0])
print(table)
print(calc_penality(table[0]))
reset_row(0, 99)
print(table)
#print(list(zip(range(1, 105), map(card_value, range(1, 105)))))
