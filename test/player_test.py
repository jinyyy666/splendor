#! /usr/local/bin/python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from board import Board
from player import Player


def test_player_sanity():
    player1 = Player(0)
    player2 = Player(1)

    assert (player1.get_id() == 0)
    assert (player2.get_id() == 1)


#def test_


if __name__ == "__main__":
    test_player_sanity()
    print("Everything passed for players!")
