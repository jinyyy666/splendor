#! /usr/local/bin/python3

import unittest

from board import Board
from player import Player
from model import (
    Gem,
) 

class PlayerTest(unittest.TestCase):


    def test_player_sanity(self):
        player1 = Player(0)
        player2 = Player(1)

        assert (player1.get_id() == 0)
        assert (player2.get_id() == 1)

        assert (player1.card_summary() == {})

    def test_pick_same_gems(self):
        my_board = Board(2)
        gems = {
            Gem.RED : 2
        }



if __name__ == "__main__":
    unittest.main()
    print("Everything passed for players!")
