#! /usr/local/bin/python3
import unittest
from copy import deepcopy

from board import Board
from model import (
    Gem,
    Card,
    Noble,
)
from player import Player


class BoardTest(unittest.TestCase):
    def test_load(self):
        b = Board(2)
        self.assertEqual(len(b.all_cards[0]), 40)
        self.assertEqual(len(b.all_cards[1]), 30)
        self.assertEqual(len(b.all_cards[2]), 20)

        self.assertEqual(len(b.all_nobles), 10)

        self.assertEqual(len(b.players), 2)

        self.assertEqual(len(b.gems), 6)

        self.assertEqual(b.gems[Gem.RED], 4)
        self.assertEqual(b.gems[Gem.GOLD], 5)

        self.assertEqual(len(b.nobles), 3)
        self.assertEqual(len(b.cards), 3)
        self.assertEqual(len(b.cards[0]), 4)

    def test_take_card(self):
        b = Board(2)
        card = b.cards[0][0]
        b.take_card(card.id)
        self.assertEqual(len(b.cards[0]), 4)

    def test_take_gems(self):
        b = Board(2)
        gems = {}
        gems[Gem.RED] = 1
        gems[Gem.GREEN] = 1
        gems[Gem.BLUE] = 1
        b.take_gems(gems)
        self.assertEqual(len(b.gems), 6)
        self.assertEqual(b.gems[Gem.RED], 3)

    def test_not_enough_gems(self):
        b = Board(2)
        gems = {}
        gems[Gem.RED] = 5
        with self.assertRaises(ValueError):
            b.take_gems(gems)

    def test_upadte_nobles(self):
        b = Board(2)
        noble = b.nobles[0]
        player = Player(1)
    
        for i in range(10):
           player.cards.add(Card(i, 1, Gem.RED, 0, {}))
           player.cards.add(Card(i, 1, Gem.GREEN, 0, {}))
           player.cards.add(Card(i, 1, Gem.BLUE, 0, {}))
           player.cards.add(Card(i, 1, Gem.WHITE, 0, {}))
           player.cards.add(Card(i, 1, Gem.BLACK, 0, {}))
        
        b._check_and_update_nobles(player)
        self.assertEqual(len(player.nobles), 1)
        self.assertEqual(next(iter(player.nobles)), noble)


    def test_payback_gems(self):
        b = Board(2)
        player = Player(0)
        original_board_gems = deepcopy(b.get_gems())

        card = b.get_cards()[0][0]

        # let the player takes the gems first and pay it back
        player.pick_different_gems(card.cost, None, b)
        b.payback_gems(card.cost)
        current_gems = b.get_gems()

        for gem, cnt in current_gems.items():
            self.assertEqual(cnt, original_board_gems[gem])


if __name__ == "__main__":
    unittest.main()
