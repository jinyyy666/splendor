import unittest

from board import Board
from player import Player
from model import (
    Gem,
    Card,
) 

from strategies.naive_strategy import NaiveStrategy


class NaiveStrategyTest(unittest.TestCase):
    def _setup_naive_strategy(self):
        my_board = Board(2)
        player = Player(0)

        
        stgy = NaiveStrategy(my_board, player)
        return stgy

    def _gen_dummy_cards(self):
        return [
            [
                Card(0, 1, Gem.GREEN, 0, {Gem.GREEN : 1, Gem.RED : 1, Gem.BLACK : 1, Gem.WHITE : 1}),
                Card(1, 1, Gem.BLACK, 0, {Gem.BLUE  : 1, Gem.RED : 1, Gem.GREEN : 2}),
                Card(2, 1, Gem.RED, 0, {Gem.GREEN : 1, Gem.RED : 2, Gem.WHITE : 1}),
                Card(3, 1, Gem.BLUE, 0, {Gem.BLUE : 1, Gem.RED : 1, Gem.WHITE : 1, Gem.BLACK: 1}),
            ],
            [
                Card(4, 2, Gem.GREEN, 1, {Gem.GREEN : 3, Gem.RED : 2, Gem.BLACK : 2}),
                Card(5, 2, Gem.WHITE, 2, {Gem.GREEN : 4, Gem.RED : 1, Gem.BLACK : 3, Gem.WHITE: 1}),
                Card(6, 2, Gem.BLACK, 3, {Gem.BLACK : 3, Gem.RED : 3, Gem.BLUE  : 5}),
                Card(7, 2, Gem.BLUE,  1, {Gem.GREEN : 3, Gem.RED : 1, Gem.BLACK : 1}),
            ],
            [
                Card(8, 3, Gem.GREEN, 4, {Gem.GREEN : 5, Gem.RED : 3, Gem.BLACK : 4, Gem.WHITE: 2}),
                Card(9, 3, Gem.WHITE, 4, {Gem.GREEN : 1, Gem.RED : 1, Gem.BLACK : 1}),
                Card(10, 3, Gem.BLUE,  5, {Gem.BLUE  : 2, Gem.GREEN : 4, Gem.BLACK : 3}),
                Card(11, 3, Gem.GREEN, 6, {Gem.WHITE : 5, Gem.RED : 3, Gem.RED : 3}),
            ],
        ]

    def test_recommend_gems_to_pick(self):
        stgy = self._setup_naive_strategy()
        my_board = Board(2)

        all_cards = self._gen_dummy_cards()

        gems_to_pick = stgy.recommend_gems_to_pick(all_cards, my_board.get_gems())

        self.assertEqual(gems_to_pick[Gem.GREEN], 1)
        self.assertEqual(gems_to_pick[Gem.RED], 1)
        self.assertEqual(gems_to_pick[Gem.BLACK], 1)

if __name__ == "__main__":
    unittest.main()
    print("Everything passed for strategies!")