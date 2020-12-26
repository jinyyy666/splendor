#! /usr/local/bin/python3

from enum import Enum
from player import Player
from model import (
    Gem,
    Card,
    Noble,
)
from util import greater_than_or_equal_to
import csv
import random
import json


class Board(object):
    def __init__(self, players_cnt, should_shuffle=False):
        self.players_cnt = players_cnt
        self.all_cards = []
        self.all_nobles = []
        self.cards_index = [0, 0, 0]
        self.noble_index = 0
        self.cards = []

        self.cards_map = {}
        self.nobles = []
        self.gems = {}
        self.players = []

        self._load(should_shuffle)

    def get_gems(self):
        '''Returns current gems showing on the board'''
        return self.gems

    def take_gems(self, gems):
        '''Takes gems from the board'''
        if not greater_than_or_equal_to(self.gems, gems):
            raise ValueError("not enough gems")
        for gem, cnt in gems.items():
            self.gems[gem] -= cnt

    def get_cards(self):
        '''Returns current development cards showing on the board'''
        return self.cards

    def get_card(self, id):
        '''Returns a developement card for a given id'''
        return self.cards_map.get(id, None)

    def take_card(self, id):
        '''Takes a card from the board'''
        if id not in self.cards_map:
            raise ValueError("invalid card_id")
        card = self.cards_map[id]
        level = card.level
        for i in range(4):
            if (self.cards[level][i].id == id):
                del self.cards[level][i]
                if self.cards_index[level] < len(self.all_cards[level]):
                    self.cards[level].append(self.all_cards[level][self.cards_index[level]])
                    self.cards_index[level] += 1
                break

    def get_nobles(self):
        '''Returns current nobles showing on the board'''
        return self.nobles

    def _load(self, should_shuffle):
        self._load_all_cards()
        self._load_all_nobles()
        if should_shuffle:
            self._shuffle()
        self._init_players()
        self._init_gems()
        self._init_cards()
        self._init_nobles()

    def _init_players(self):
        '''Initiates players for the board to start the game'''
        for i in range(0, self.players_cnt):
            self.players.append(Player(i))
        
    def _shuffle(self):
        '''Shuffle cards and nobles'''
        for cards in self.all_cards:
            random.shuffle(cards)
        
        random.shuffle(self.all_nobles)

    def _init_cards(self):
        '''Initiates development cards for the board to start the game'''
        for i in range(3):
            self.cards.append([])
            for _ in range(4):
                self.cards[i].append(self.all_cards[i][self.cards_index[i]])
                self.cards_index[i] += 1

    def _init_gems(self):
        '''Initiates gems for the board to start the game'''
        assert self.players_cnt >= 2 and self.players_cnt <= 4
        for gem_type in Gem:
            if self.players_cnt == 4:
                self.gems[gem_type] = 7
            else:
                self.gems[gem_type] = 2 + self.players_cnt
        self.gems[Gem.GOLD] = 5

    def _init_nobles(self):
        '''Initiates nobles for the board to start the game'''
        for _ in range(self.players_cnt + 1):
            self.nobles.append(self.all_nobles[self.noble_index])
            self.noble_index += 1

    def _load_all_cards(self):
        '''Loads all development cards from CSV file'''
        fo = open('config/cards.csv')
        reader = csv.reader(fo)
        next(reader, None) # skip header
        id = 0
        for _ in range(3):
            self.all_cards.append([])

        for line in reader:
            assert len(line) == 8
            level = int(line[0])
            card = Card(
                id, level, Gem._value2member_map_[line[1]], int(line[2]),
                self._get_cost([gem for gem in Gem], line[3:]))
            self.all_cards[level - 1].append(card)
            self.cards_map[id] = card
            id += 1
        fo.close()

    def _load_all_nobles(self):
        '''Loads all nobles from CSV file'''
        fo = open('config/nobles.csv')
        reader = csv.reader(fo)
        next(reader, None) # skip header
        id = 0
        for line in reader:
            assert len(line) == 6
            noble = Noble(id, int(line[2]), self._get_cost([gem for gem in Gem], line[1:]))
            id += 1
            self.all_nobles.append(noble)
        fo.close()

    def _get_cost(self, gems, values):
        cost = {}
        for gem, count in zip(gems[:-1], values):
            if len(count) == 0:
                continue
            cost[gem] = int(count)
        return cost

    def _check_and_update_nobles(self, player):
        '''Checks all nobles and take if possible'''
        idx_to_remove = -1
        nobles = self.nobles
        for i in range(len(nobles)):
            if nobles[i].can_attract(player.card_summary()):
                player.attract_noble(nobles[i])
                idx_to_remove = i
                break
        if idx_to_remove >= 0:
            del nobles[i]

if __name__ == '__main__':
    board = Board(2)
    can_win = False
    while not can_win:
        for player in board.players:
            player.take_action(board)
            board._check_and_update_nobles(player)
            if player.can_win():
                can_win = True
    if can_win:
        board.players.sort(key=lambda p: (-p.reputation, p.development_cards))
        print('Player {} won!'.format(board.players[0].id))
