from enum import Enum
import csv
import random


class Gem(Enum):
    RED = 'r'
    GREEN = 'g'
    BLUE = 'b'
    WHITE = 'w'
    BLACK = 'k'
    GOLD = 'o'

class Card:
    def __init__(self, id, level, gem, reputation, cost):
        self.id = id
        self.level = level
        self.gem = gem
        self.reputation = reputation
        self.cost = cost

class Noble:
    def __init__(self, id, reputation, cost):
        self.id = id
        self.reputation = reputation
        self.cost = cost

    def track_player(player):
        '''Tracks whether a player has gained the notice'''

        return True


class Board:
    def __init__(self, players_cnt):
        self.players_cnt = players_cnt
        self.all_cards = [[], [], []]
        self.all_nobles = []
        self.cards_index = [0, 0, 0]
        self.noble_index = 0

        self.cards = [[], [], []]
        self.nobles = []

        self._load_all_cards()
        self._load_all_nobles()

        self._init_cards()

    def get_cards(self):
        cards = []
        for list in self.cards:
            cards += list
        return set(cards)

    def get_nobles(self):

        return

    def _init_cards(self):
        '''Initiates development cards for the board to start the game'''
        for i in range(0, 3):
            for j in range(0, 4):
                print(self.all_cards[i][self.cards_index[i]])
                self.cards[i].append(self.all_cards[i][self.cards_index[i]])
                self.cards_index[i] += 1

    def _load_all_cards(self):
        '''Loads all development cards from CSV file'''
        reader = csv.reader(open('cards.csv'))
        next(reader, None) # skip header
        id = 0
        for line in reader:
            assert len(line) == 8
            level = int(line[0])
            card = Card(
                id, level, line[1], int(line[2]),
                self._get_cost([c.value for c in Gem], line[3:]))
            self.all_cards[level - 1].append(card)
            id += 1
        for cards in self.all_cards:
            random.shuffle(cards)

    def _load_all_nobles(self):
        '''Loads all nobles from CSV file'''
        reader = csv.reader(open('nobles.csv'))
        next(reader, None) # skip header
        id = 0
        for line in reader:
            assert len(line) == 6
            level = int(line[0])
            noble = Noble(id, int(line[2]), self._get_cost([c.value for c in Gem], line[1:]))
            id += 1
            self.all_nobles.append(noble)
        random.shuffle(self.all_nobles)

    def _get_cost(self, gems, values):
        cost = {}
        for gem, count in zip(gems[:-1], values):
            if len(count) == 0:
                continue
            cost[gem] = int(count)
        return cost

if __name__ == '__main__':
    board = Board(2)
