import functools, operator, math
from strategies.strategy import Strategy
from copy import deepcopy

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


class CardValue(object):
    def __init__(self, card_id, card_rep, can_afford, value, dist, req_gems):
        self.card_id = card_id
        self.card_reputation = card_rep
        self.can_afford = can_afford
        self.value = value
        self.dist = dist
        self.req_gems = req_gems

'''
Aggressive Strategy:
- It looks at other players as well
- It will try to collect the most common gems
- It will try to purchase the cards from low to high if it can afford
'''
class AggressiveStrategy(Strategy):
    def __init__(self, board, player):
        self.steps = 0
        self.player = player
        #self.other_players = other_players
        super().__init__(board, [player])

    ## just pick the top three most common gems
    def recommend_gems_to_pick(self, gems_on_board, sorted_card_values):
        gem_scores = {gem : 0 for gem in Gem}

        for c_v in sorted_card_values:
            for g, c in c_v.req_gems.items():
                if g == Gem.GOLD:
                    import pdb; pdb.set_trace()

                gem_scores[g] += math.log(1 + c_v.value) * c

        sorted_v = sorted(gem_scores.items(), key=lambda kv: kv[1], reverse=True)
        gems_to_pick = {}
        
        for gem, _ in sorted_v:
            if gem == Gem.GOLD:
                continue
            if gems_on_board[gem] > 0:
                if gem == Gem.GOLD:
                    import pdb; pdb.set_trace()
                gems_to_pick[gem] = 1
            if len(gems_to_pick) == 3:
                break
        
        return gems_to_pick


    def compute_distance(self, eff_gems, cost):
        gems_to_pay = {}
        gold_count = eff_gems.get(Gem.GOLD, 0)
        dist = 0
        for g, v in cost.items():
            eff_gem = eff_gems.get(g, 0)
            if (eff_gem < v):
                dist += v - eff_gem
                gems_to_pay[g] = v - eff_gem
        
        dist = max(0, dist - gold_count)
        if gold_count > 0:
            for g, c in gems_to_pay.items():
                if c > 0:
                    while (gold_count > 0) and (gems_to_pay[g] > 0):
                        gems_to_pay[g] -= 1
                        gold_count -= 1
                if gold_count == 0:
                    break

        cost_to_pay = 0
        for _, c in gems_to_pay.items():
            cost_to_pay += c
        
        if dist != cost_to_pay:
            import pdb; pdb.set_trace()

        assert (dist == cost_to_pay)
        return dist, gems_to_pay


    def get_card_value(self, card_gem, card_rep, can_afford, dist, ply_card_summary):
        aff_score = 2 if can_afford else 0
        dist_score = math.exp(-1 * dist)

        sum_c = 0
        n_c = 0
        for g, c in ply_card_summary.items():
            if c > 0:
                n_c += 1
                sum_c += c

        mean_c = 0 if n_c == 0 else 1.0 * sum_c / n_c
        var_new = 0
        var_old = 0

        for g, c in ply_card_summary.items():
            if c > 0:
                var_old += abs(c - mean_c) ** 2
                if g != card_gem:
                    var_new += abs(c - mean_c) ** 2
                else:
                    var_new += abs((c + 1) - mean_c) ** 2

        card_gem_score = 1 if var_old > var_new else 0
        card_rep_score = math.log( 1 + card_rep )
        return aff_score + dist_score + card_gem_score + card_rep_score


    def get_current_cards_summary(self, cards):
        summary = []
        eff_gems = self.player.card_summary_plus_current_gems()
        ply_card_summary = self.player.card_summary()

        for card in cards:
            dist, diff = self.compute_distance(eff_gems, card.cost)
            can_afford = self.player.can_afford(card)
            value = self.get_card_value(card.gem, card.reputation, can_afford, dist, ply_card_summary)
            summary.append(CardValue(card.id, card.reputation, can_afford, round(value, 2), dist, diff))

        return summary

    def next_step(self):
        # print(f'In step: {self.steps}')
        self.steps = self.steps + 1
        cards = self.board.get_cards()
        cards_list = functools.reduce(operator.iconcat, cards, [])

        gems_on_board = self.board.get_gems()

        # get a collective view of the current cards
        # try to get the best value one
        # if we cannot buy, we just fetch the gems so that we can buy it later
        card_values = self.get_current_cards_summary(cards_list)

        sorted_card_vals = sorted(card_values, key=lambda c: c.value, reverse=True)

        # only for debugging:
        # print([ (c.card_id, c.card_reputation, c.can_afford, c.value, c.req_gems, c.dist) for c in sorted_card_vals ])

        # try to buy the top 5 cards
        for sorted_value in sorted_card_vals[:5]:
            if sorted_value.can_afford:
                # print(f'buy card: {sorted_value.card_id}')
                return ActionParams(self.player.id, Action.BUY_CARD, None, sorted_value.card_id)
        
        # if we cannot afford them, let's collect gems to get closer
        gems_to_pick = self.recommend_gems_to_pick(gems_on_board, sorted_card_vals[:5])
        if greater_than_or_equal_to(gems_on_board, gems_to_pick) and len(gems_to_pick) > 0:
            # print(f'pick three gems - 1: {gems_to_pick}')
            return ActionParams(self.player.id, Action.PICK_THREE, gems_to_pick, None)
        else:
            # print(f'Reserve card: {cards_list[0].id}')
            return ActionParams(self.player.id, Action.RESERVE_CARD, None, cards_list[0].id)
