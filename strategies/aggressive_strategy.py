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
    def __init__(self, card_id, can_afford, value, dist, req_gems):
        self.card_id = card_id
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
    def recommend_gems_to_pick(self, all_cards, gems_on_board):
        def _lvl_score(lvl):
            return math.exp(-1 * lvl)

        gem_scores = {gem : 0 for gem in Gem}
        for lvl, cards in enumerate(all_cards):
            for card in cards:
                for g, cnt in card.cost.items():
                    gem_scores[g] += cnt * _lvl_score(lvl)

        sorted_x = sorted(gem_scores.items(), key=lambda kv: kv[1], reverse=True)
        gems_to_pick = {}
        for gem, _ in sorted_x:
            if gems_on_board[gem] > 0:
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


    def get_card_value(self, card_gem, can_afford, dist, ply_card_summary):
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

        return aff_score + dist_score + card_gem_score


    def get_current_cards_summary(self, cards):
        summary = []
        eff_gems = self.player.card_summary_plus_current_gems()
        ply_card_summary = self.player.card_summary()

        for card in cards:
            dist, diff = self.compute_distance(eff_gems, card.cost)
            can_afford = self.player.can_afford(card)
            value = self.get_card_value(card.gem, can_afford, dist, ply_card_summary)
            summary.append(CardValue(card.id, can_afford, value, dist, diff))

        return summary

    def next_step(self):
        #print(f'In step: {self.steps}')
        self.steps = self.steps + 1
        cards = self.board.get_cards()
        cards_list = functools.reduce(operator.iconcat, cards, [])
        gems_on_board = self.board.get_gems()

        # get a collective view of the current cards
        # try to get the best value one
        # if we cannot buy, we just fetch the gems so that we can buy it later
        card_values = self.get_current_cards_summary(cards_list)

        sorted_card_vals = sorted(card_values, key=lambda c: c.value, reverse=True)

        selected_card_stat = sorted_card_vals[0]

        if selected_card_stat.can_afford:
            #print(f'buy card: {selected_card_stat.card_id}')
            return ActionParams(Action.BUY_CARD, None, selected_card_stat.card_id)
        else:
            req_gems = selected_card_stat.req_gems
            gems_to_pick = deepcopy(req_gems)
            
            distance = selected_card_stat.dist
            if distance > 3:
                for g, c in req_gems.items():
                    if c > 1:
                        gems_to_pick[g] -= 1
            elif distance < 3:
                total = distance
                for g in Gem:
                    if g == Gem.GOLD:
                        continue
                    if g not in gems_to_pick:
                        gems_to_pick[g] = 1
                        total += 1
                    if total == 3:
                        break
            if greater_than_or_equal_to(gems_on_board, gems_to_pick):
                return ActionParams(Action.PICK_THREE, gems_to_pick, None)
            else:
                #import pdb; pdb.set_trace()
                if len(self.player.get_rev_cards()) == 3:
                    gems_to_pick = self.recommend_gems_to_pick(cards, gems_on_board)
                    return ActionParams(Action.PICK_THREE, gems_to_pick, None)
                else:
                    return ActionParams(Action.RESERVE_CARD, None, cards_list[0].id)

            #return ActionParams(Action.PICK_THREE, gems_to_pick, None)
