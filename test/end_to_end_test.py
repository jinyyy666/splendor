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
        action_params = []
        with open('test/data/actions.json') as f:
            data = json.load(f)
            actions = data['actions']
            for action in actions:
                action_params.append(self._convert(action))

        b = Board(2, False, 0)
        b.nobles[0] = Noble(0, 3, {Gem.BLACK: 2})
        players = b.players
        player_idx = 0
        for action in action_params:
            player = players[player_idx]
            player.take_external_action(action, b)
            b._check_and_update_nobles(player)
            player_idx = 1 - player_idx

        self.assertEqual(len(players[0].cards), 2)
        self.assertEqual(len(players[1].cards), 1)
        self.assertEqual(players[0].rep, 3)
        self.assertEqual(players[1].rep, 0)
        self.assertEqual(len(b._get_winners()), 1)
        self.assertEqual(b._get_winners()[0], players[0])
    
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