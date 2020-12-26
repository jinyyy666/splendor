#! /usr/local/bin/python3

from board import Board
from model import Gem

import unittest


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


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
