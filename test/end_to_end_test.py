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

        for action in actions:
            actions = self._convert(action)

        b = Board(2, False)
        players = b.players
        player_idx = 0
        for action in actions:
            player = players[player_idx]
            player_idx = ~player_idx

    
    def _convert(self, obj):
        action = Action[obj['action']]
        gems = []
        if 'gems' in obj:
            for gem in obj['gems']:
                gems.append(Gem[gem])
        card_id = -1
        if 'card' in obj:
            card_id = int(obj['card'])
        return ActionParams(action, gems, card_id)

if __name__ == "__main__":
    unittest.main()