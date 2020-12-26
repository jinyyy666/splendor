#! /usr/local/bin/python3

import unittest
from copy import deepcopy

from board import Board
from player import Player
from model import (
    Gem,
) 

class PlayerTest(unittest.TestCase):
    def _check_board_gems(self, current_gems, orginal_gems):
        for gem, cnt in current_gems.items():
            self.assertEqual(cnt, orginal_gems[gem])

    def test_player_sanity(self):
        player1 = Player(0)
        player2 = Player(1)

        self.assertEqual(player1.get_id(), 0)
        self.assertEqual(player2.get_id(), 1)
        
        self.assertEqual(player1.card_summary(), {})

    def test_pick_same_gems(self):
        my_board = Board(2)
        
        player1 = Player(0)
        player2 = Player(1)

        gems = {
            Gem.RED : 2
        }
        player1.pick_same_gems(gems, None, my_board)
        self.assertEqual(player1.get_gems()[Gem.RED], 2)
        self.assertEqual(player2.get_gems()[Gem.RED], 0)

        self.assertEqual(my_board.get_gems()[Gem.RED], 2)
        self.assertEqual(my_board.get_gems()[Gem.GREEN], 4)
        self.assertEqual(my_board.get_gems()[Gem.BLUE], 4)
        self.assertEqual(my_board.get_gems()[Gem.WHITE], 4)
        self.assertEqual(my_board.get_gems()[Gem.BLACK], 4)

        gems = {
            Gem.BLUE : 2
        }
        player2.pick_same_gems(gems, None, my_board)
        self.assertEqual(player2.get_gems()[Gem.BLUE], 2)
        self.assertEqual(player1.get_gems()[Gem.BLUE], 0)

        self.assertEqual(my_board.get_gems()[Gem.BLUE], 2)
        self.assertEqual(my_board.get_gems()[Gem.RED], 2)
        self.assertEqual(my_board.get_gems()[Gem.GREEN], 4)
        self.assertEqual(my_board.get_gems()[Gem.WHITE], 4)
        self.assertEqual(my_board.get_gems()[Gem.BLACK], 4)


    def test_pick_different_gems(self):
        my_board = Board(2)
        
        player1 = Player(0)
        player2 = Player(1)

        gems = {
            Gem.RED : 1,
            Gem.GREEN : 1, 
            Gem.BLACK : 1,
        }
        player1.pick_different_gems(gems, None, my_board)
        self.assertEqual(player1.get_gems()[Gem.RED], 1)
        self.assertEqual(player1.get_gems()[Gem.GREEN], 1)
        self.assertEqual(player1.get_gems()[Gem.BLACK], 1)

        self.assertEqual(my_board.get_gems()[Gem.RED], 3)
        self.assertEqual(my_board.get_gems()[Gem.GREEN], 3)
        self.assertEqual(my_board.get_gems()[Gem.BLACK], 3)
        self.assertEqual(my_board.get_gems()[Gem.BLUE], 4)
        self.assertEqual(my_board.get_gems()[Gem.WHITE], 4)

        
        gems = {
            Gem.BLUE : 1,
            Gem.GREEN : 1, 
            Gem.BLACK : 1,
        }
        player2.pick_different_gems(gems, None, my_board)
        self.assertEqual(player2.get_gems()[Gem.BLUE], 1)
        self.assertEqual(player2.get_gems()[Gem.GREEN], 1)
        self.assertEqual(player2.get_gems()[Gem.BLACK], 1)

        self.assertEqual(my_board.get_gems()[Gem.BLUE], 3)
        self.assertEqual(my_board.get_gems()[Gem.GREEN], 2)
        self.assertEqual(my_board.get_gems()[Gem.BLACK], 2)
        self.assertEqual(my_board.get_gems()[Gem.RED], 3)
        self.assertEqual(my_board.get_gems()[Gem.WHITE], 4)

        gems = {
            Gem.BLACK: 3,
        }
        with self.assertRaises(ValueError):
            player1.pick_same_gems(gems, None, my_board)
        

    def test_buy_board_card(self):
        my_board = Board(2)
        orginal_board_gems = deepcopy(my_board.get_gems())

        player1 = Player(0)
        cards = my_board.get_cards()

        # get level 1 card
        card = cards[0][0]
        expensive_card = cards[2][0]

        # just let player1 pick enough gems to buy the card
        player1.pick_different_gems(card.cost, None, my_board)

        player1.buy_board_card(None, card, my_board)
        self.assertEqual(player1.get_cards(), {card})
        self.assertEqual(player1.card_summary()[card.gem], 1)

        # check if board gems are back to initial value
        current_gems = my_board.get_gems()
        self._check_board_gems(current_gems, orginal_board_gems)

        # try to buy without any gems at hand:
        with self.assertRaises(ValueError):
            player1.buy_board_card(None, expensive_card, my_board)


    def test_reserve_card(self):
        my_board = Board(2)
        
        player1 = Player(0)
        cards = my_board.get_cards()

        # get level 1 card
        card = cards[0][1]

        player1.reserve_card(None, card, my_board)

        self.assertEqual(player1.get_gems()[Gem.GOLD], 1)
        self.assertEqual(player1.get_rev_cards(), {card})
        self.assertEqual(player1.reserve_count, 1)

        # try to reverse more:
        player1.reserve_card(None, cards[1][0], my_board)
        player1.reserve_card(None, cards[1][1], my_board)
        with self.assertRaises(ValueError):
            player1.reserve_card(None, cards[2][0], my_board)


    def test_buy_reserve_card(self):
        my_board = Board(2)
        orginal_board_gems = deepcopy(my_board.get_gems())
        player1 = Player(0)
        cards = my_board.get_cards()

        # get level 1 card and reserve it
        card = cards[0][0]
        
        player1.reserve_card(None, card, my_board)

        cost = deepcopy(card.cost)
        # test if we can use the gold
        for g, c in cost.items():
            if c > 0:
                cost[g] -= 1
                break

        player1.pick_different_gems(cost, None, my_board)
        player1.buy_reserve_card(None, card, my_board)
        self.assertEqual(player1.get_cards(), {card})
        self.assertEqual(player1.card_summary()[card.gem], 1)
        self.assertEqual(player1.reserve_count, 0)

        # check if board gems are back to initial value
        current_gems = my_board.get_gems()
        self._check_board_gems(current_gems, orginal_board_gems)


    def test_reserve_card_and_buy_card(self):
        my_board = Board(2)
        player1 = Player(0)
        cards = my_board.get_cards()

        # get level 1 card and reserve it
        card1 = cards[0][0]
        card2 = cards[0][1]

        player1.reserve_card(None, card1, my_board)
        player1.reserve_card(None, card2, my_board)
        self.assertEqual(player1.reserve_count, 2)

        card = cards[0][2]

        cost = deepcopy(card.cost)
        # test if we can use two golds to buy a simple card
        times = 2
        for g, c in cost.items():
            if c > 0 and times > 0:
                cost[g] -= 1
                times -= 1
    
        player1.pick_different_gems(cost, None, my_board)
        player1.buy_board_card(None, card, my_board)
        self.assertEqual(player1.get_cards(), {card})

    def test_buy_card_and_use_card_gem(self):
        my_board = Board(2)
        orginal_board_gems = deepcopy(my_board.get_gems())

        player1 = Player(0)
        cards = my_board.get_cards()

        # just let player1 pick enough gems and use them to buy cards
        for i in range(4):
            card = cards[0][i]
            
            player1.pick_different_gems(card.cost, None, my_board)
            player1.buy_board_card(None, card, my_board)

        card = my_board.get_cards()[0][0]

        cost = deepcopy(card.cost)
        card_summary = player1.card_summary()
        # use the gems to adjust the cost
        for g, c in cost.items():
            c = min(0, c - card_summary.get(g, 0))
        
        player1.pick_different_gems(cost, None, my_board)
        player1.buy_board_card(None, card, my_board)
        self.assertEqual(len(player1.get_cards()), 5)

        # check if board gems are back to initial value
        current_gems = my_board.get_gems()
        self._check_board_gems(current_gems, orginal_board_gems)
        

if __name__ == "__main__":
    unittest.main()
    print("Everything passed for players!")
