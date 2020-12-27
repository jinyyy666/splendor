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
Smart Strategy:
- It will try to find the easiet to get gem each round
- It will look at the other players and try to grab the card they want to purchase
- It will try to purchase the cards from high to low if it can afford
- It will try to attract nobles
'''
class SmartStrategy(Strategy):
    def __init__(self, board, player):
        self.player = player
        self.steps = 0
        super().__init__(board, [player])

    ## just pick the top three most common gems
    def recommend_gems_to_pick(self, all_cards, gems_on_board, current_gems):
        def _lvl_score(lvl):
            return math.exp(-1 * lvl)

        def gems_needed(card, current_gems):
            gems = {}
            needed = 0
            for g, cnt in card.cost.items():
                if current_gems[g] < cnt:
                    diff = cnt - current_gems[g]
                    gems[g] = gems.get(g, 0) + diff
                    needed += diff
            return gems, needed

        def analyze_gems(gems):
            for _, cnt in gems.items():
                if cnt > 1:
                    return False
            return True

        gem_scores = {gem : 0 for gem in Gem}
        for lvl, cards in enumerate(all_cards):
            for card in cards:
                for g, cnt in card.cost.items():
                    gem_scores[g] += cnt * _lvl_score(lvl)
        
        candidates = {}
        needs = {}
        for lvl, cards in enumerate(all_cards):
            for card in cards:
                gems, needed = gems_needed(card, current_gems)
                if analyze_gems(gems):
                    candidates[card.id] = (1.0 * card.reputation) / needed
                    needs[card.id] = gems
        
        gems_to_pick = {}
        sorted_cards = sorted(candidates.items(), key=lambda kv: kv[1])
        for card_id, _ in sorted_cards:
            for gem in needs[card_id]:
                if len(gems_to_pick) == 3:
                    break
                if gems_on_board[gem] > 0:
                    gems_to_pick[gem] = 1


        sorted_x = sorted(gem_scores.items(), key=lambda kv: kv[1], reverse=True)
        for gem, _ in sorted_x:
            if len(gems_to_pick) == 3:
                break
            if gems_to_pick.get(gem, 0) == 1 or gem == Gem.GOLD:
                continue
            if gems_on_board[gem] > 0:
                gems_to_pick[gem] = 1
        
        if len(gems_to_pick) < 3:
            for gem in Gem:
                if len(gems_to_pick) == 3:
                    break
                if gem == Gem.GOLD:
                    continue
                if gems_on_board[gem] and gems_to_pick.get(gem, 0) == 0:
                    gems_to_pick[gem] = 1
                

        return gems_to_pick


    def next_step(self):
        # print(f'In step: {self.steps}')
        self.steps = self.steps + 1
        cards = self.board.get_cards()
        cards_list = functools.reduce(operator.iconcat, cards, [])
        cards_list.reverse()
        gems_on_board = self.board.get_gems()
        current_gems = self.player.card_summary_plus_current_gems()

        for card in cards_list:
            # just buy the card if it can afford
            if self.player.can_afford(card):
                return ActionParams(self.player.id, Action.BUY_CARD, None, card.id)

        # if you cannot afford anything, get gems if possible:
        gems_to_pick = self.recommend_gems_to_pick(cards, gems_on_board, current_gems)
        if greater_than_or_equal_to(gems_on_board, gems_to_pick) and len(gems_to_pick) > 0:
            return ActionParams(self.player.id, Action.PICK_THREE, gems_to_pick, None)
        else:
            #import pdb; pdb.set_trace()
            return ActionParams(self.player.id, Action.RESERVE_CARD, None, cards_list[0].id)

