#! /usr/local/bin/python3

from enum import Enum
import csv
import random
from util import greater_than_or_equal_to


class Gem(Enum):
    RED = 'r'
    GREEN = 'g'
    BLUE = 'b'
    WHITE = 'w'
    BLACK = 'k'
    GOLD = 'o'

class Card(object):
    def __init__(self, id, level, gem, reputation, cost):
        self.id = id
        self.level = level
        self.gem = gem
        self.reputation = reputation
        self.cost = cost

class Noble(object):
    def __init__(self, id, reputation, cost):
        self.id = id
        self.reputation = reputation
        self.cost = cost

    def can_attract(self, card_summary):
        '''Returns whether a player can attract the noble'''
        return greater_than_or_equal_to(card_summary, self.cost)
