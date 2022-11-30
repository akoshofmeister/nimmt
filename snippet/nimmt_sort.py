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
    # print table
    return query_user(list(range(4)))


# def select_card():
#	return query_user(hand)




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
            pass;  # print('ok')
        else:
            print(card, ': select a row!')
            selection = select_row()
            reset_row(selection, card)


def card_value(card):
    for l, n in zip([55, 11, 10, 5], [7, 5, 3, 2]):
        if card % l == 0:
            return n
    return 1


def calc_penality(row):
    return sum(map(card_value, row))


# place_all_cards([3, 10, 35, 34])
# print(table)
# table.sort(key=lambda x: x[0])
# print(table)
print(calc_penality(table[2]))
reset_row(0, 99)
print(table)
# print(list(zip(range(1, 105), map(card_value, range(1, 105)))))
