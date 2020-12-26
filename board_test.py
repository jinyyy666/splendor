#! /usr/local/bin/python3

from board import Board
from model import Gem


def test_load():
    b = Board(2)
    assert len(b.all_cards[0]) == 40
    assert len(b.all_cards[1]) == 30
    assert len(b.all_cards[2]) == 20

    assert len(b.all_nobles) == 10

    assert len(b.players) == 2

    assert len(b.gems) == 6
    assert b.gems[Gem.RED] == 4
    assert b.gems[Gem.GOLD] == 5

    assert len(b.nobles) == 3

    assert len(b.cards) == 3
    assert len(b.cards[0]) == 4

def test_take_card():
    b = Board(2)
    card = b.cards[0][0]
    b.take_card(card.id)
    assert len(b.cards[0]) == 4


if __name__ == "__main__":
    test_load()
    test_take_card()
    print("Everything passed")
