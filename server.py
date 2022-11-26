#!usr/bin/python
import random
import json

from board import Board
from player import Player

all_players = {}
board = None
ALL_CARDS_COUNT = 104


def broadcast(client_list, data):
    jsondata = bytes(data, 'utf-8')
    for c in client_list:
        c.send(jsondata)


def modifyPlayerList(playerOperation, client):
    if "ACCEPT" == playerOperation:
        all_players[client] = Player(client)
    else:
        del all_players[client]


def process_data(client, data_in_bytes, playerOperation):
    if playerOperation:
        modifyPlayerList(playerOperation, client)
        return
    data = str(data_in_bytes, 'utf-8').strip()

    # broadcast(list(all_players.keys()), data)
    is_start = data == "start"
    is_give_card = data[0] == 'g'
    if is_start:
        cards = list(range(1, ALL_CARDS_COUNT))
        random.shuffle(cards)

        for player in all_players.values():
            player.set_hand(cards[:10])
            cards = cards[10:]

        board = Board(cards[:4])
        data = json.dumps(board.rows)
        broadcast(list(all_players.keys()), data)
    elif is_give_card:
        current_cards = int(data[1:])
        if all_players[client].set_card(current_cards) == None:
            send_json='{"Not in your hand":' + str(current_cards) + '}'
            broadcast([client], send_json)
            return

        current_cards = [p.card for p in all_players.values() if p.card]

        if len(current_cards) == len(all_players):
            broadcast(list(all_players.keys()), "megvagyunk")
    else:
        print('unknown ' + data)
