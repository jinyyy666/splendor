#! /usr/local/bin/python3

from board import Board


def test_board():
    # import pdb; pdb.set_trace()
    b = Board(2)
    assert len(b.get_gems()) == 6, "Gems count should be 6"
    assert len(b.get_gems()) == 6, "Gems count should be 6"

if __name__ == "__main__":
    test_board()
    print("Everything passed")
