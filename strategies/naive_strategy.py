import functools, operator, math
from strategies.strategy import Strategy

from player import (
    Action,
    ActionParams,
)

from model import (
    Gem
)

from util import (
    greater_than_or_equal_to
)

'''
Naive Strategy:
- It only looks at the player itself
- It will try to collect the most common gems
- It will try to purchase the cards from low to high if it can afford
'''
class NaiveStrategy(Strategy):
    def __init__(self, board, player):
        self.player = player
        super().__init__(board, [player])

    ## just pick the top three most common gems
    def recommend_gems_to_pick(self, all_cards):
        def _lvl_score(lvl):
            return math.exp(-1 * lvl)

        gem_scores = {gem : 0 for gem in Gem}
        for lvl, cards in enumerate(all_cards):
            for card in cards:
                for g, cnt in card.cost.items():
                    gem_scores[g] += cnt * _lvl_score(lvl)

        sorted_x = sorted(gem_scores.items(), key=lambda kv: kv[1], reverse=True)
        gems_to_pick = {gem[0]: 1 for gem in sorted_x[:3]}
        
        return gems_to_pick


    def next_step(self):
        cards = self.board.get_cards()
        cards_list = functools.reduce(operator.iconcat, cards, [])
        gems_on_board = self.board.get_gems()

        for card in cards_list:
            # just buy the card if it can afford
            if self.player.can_afford(card):
                return ActionParams(Action.BUY_CARD, None, card.id)

        # if you cannot afford anything, get gems if possible:
        gems_to_pick = self.recommend_gems_to_pick(cards)
        if greater_than_or_equal_to(gems_on_board, gems_to_pick):
            return ActionParams(Action.PICK_THREE, gems_to_pick, None)
        else:
            return ActionParams(Action.RESERVE_CARD, None, cards_list[0])

