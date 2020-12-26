#! /usr/local/bin/python3

from board import Board
from model import (
    Gem,
    Card,
    Noble,
)
from player import (
    Player,
    Action,
    ActionParams,
)

import json
import unittest


class EndToEndTest(unittest.TestCase):

    def test_end_to_end(self):
        actions = []
        with open('test/data/actions.json') as f:
            data = json.load(f)
            actions = data['actions']

        action_params = []
        for action in actions:
            action_params.append(self._convert(action))

        b = Board(2, False)
        players = b.players
        player_idx = 0
        for action in action_params:
            player = players[player_idx]
            player.take_external_action(action, b)
            player_idx = ~player_idx

        self.assertEqual(next(iter(players[0].cards)), b.get_card(0))
        self.assertEqual(next(iter(players[1].cards)), b.get_card(1))
    
    def _convert(self, obj):
        action = Action[obj['action']]
        gems = {}
        for gem in obj.get('gems', []):
            if action == Action.PICK_THREE:
                gems[Gem[gem]] = 1
            elif action == Action.PICK_SAME:
                gems[Gem[gem]] = 2

        card_id = obj.get('card', -1)
        return ActionParams(action, gems, card_id)

if __name__ == "__main__":
    unittest.main()