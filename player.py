import functools
import itertools
import operator
import collections

from enum import Enum
from model import (
    Gem,
    Card,
    Noble,
)
from util import (
    greater_than_or_equal_to
)


class Action(Enum):
    PICK_THREE = 0
    PICK_SAME = 1
    BUY_CARD = 2
    RESERVE_CARD = 3
    BUY_RESERVE_CARD = 4
    NONE = 5


class ActionParams(object):
    def __init__(self, player_id, action, gems, card_id):
        self.player_id = player_id
        self.action = action
        self.gems = gems
        self.card_id = card_id

        self._func_map = {
            Action.PICK_THREE: self.validate_pick_three,
            Action.PICK_SAME: self.validate_pick_same,
            Action.BUY_CARD: self.validate_reserve_card,
            Action.BUY_RESERVE_CARD: self.validate_reserve_card,
            Action.RESERVE_CARD: self.validate_reserve_card,
            Action.NONE: self.no_action,
        }

        if not self._func_map[action]():
            raise ValueError(
                f"Player {self.player_id} submits invalid argument for action: {action}!! \n" + 
                f"Gem counts: {self.gems}, card to purchase: {self.card_id}"
            )

    def validate_pick_three(self):
        return len(self.gems) >= 1 and len(self.gems) <= 3 and Gem.GOLD not in self.gems

    def validate_pick_same(self):
        return len(self.gems) == 1 and Gem.GOLD not in self.gems

    def validate_reserve_card(self):
        return self.card_id >= 0 and self.card_id <= 89

    def no_action(self):
        pass

class Player(object):
    def __init__(self, id):
        self.rep = 0
        self.id = id
        self.reserve_count = 0

        # all the development cards the player has
        self.cards = set()

        # all nobles attracted by the player
        self.nobles = set()
        self.known_noble_ids = set()

        # the reversed cards
        self.rev_cards = set()

        # number of gold:
        self.gold = 0

        # the gems player has via the develop card
        self.gems_from_card = {
            gem: 0 for gem in Gem.__members__.values()
        }

        # the gems player has in hand
        self.gems_from_hand = {
            gem: 0 for gem in Gem.__members__.values()
        }

        # the function map for simplicity:
        self._func_map = {
            Action.PICK_THREE: self.pick_different_gems,
            Action.PICK_SAME: self.pick_same_gems,
            Action.BUY_CARD: self.buy_board_card,
            Action.BUY_RESERVE_CARD: self.buy_reserve_card,
            Action.RESERVE_CARD: self.reserve_card,
            Action.NONE: self.no_action,
        }

    def attract_noble(self, noble):
        assert (noble.id not in self.known_noble_ids)
        self.nobles.add(noble)
        self.known_noble_ids.add(noble.id)
        self.rep += noble.reputation


    def can_win(self, points_to_win):
        return self.rep >= points_to_win


    def can_afford(self, card):
        c_dict = collections.defaultdict(int)
        for k, v in itertools.chain(self.gems_from_card.items(), self.gems_from_hand.items()):
            c_dict[k] += v
        total_available_gems = dict(c_dict)

        gold_count = self.gems_from_hand.get(Gem.GOLD, 0)
        for gem_t, cnt in card.cost.items():
            availb = total_available_gems[gem_t]
            if cnt > availb:
                if cnt > availb + gold_count:
                    return False
                else:
                    gold_count = gold_count - (cnt - availb)
                    assert (gold_count >= 0)
        return True


    ## getters:
    def get_id(self):
        return self.id

    def get_gems(self):
        return self.gems_from_hand

    def get_cards(self):
        return self.cards

    def get_rev_cards(self):
        return self.rev_cards

    ## setters:
    def set_gems(self, gems):
        self.gems_from_hand = gems

    def set_strategy(self, strategy):
        self.strategy = strategy

    def _add_gems(self, gems):
        for gem_t, cnt in gems.items():
            self.gems_from_hand[gem_t] += cnt


    def card_summary(self):
        summary = {gem : 0 for gem in Gem}
        for c in self.cards:
            if c.gem not in summary:
                summary[c.gem] = 0
            summary[c.gem] += 1
        return summary


    def card_summary_plus_current_gems(self):
        summary = self.card_summary()
        
        for g, c in self.gems_from_hand.items():
            if g in summary:
                summary[g] += c
        return summary


    # ---------------------------------------------------------
    # Here are all the standard operations the player can take
    # 1. pick three different gems
    # 2. pick two gems if there are 4 gems given a kind
    # 3. buy a development card
    # 4. reserve a development card and get a gold
    # ---------------------------------------------------------
    def pick_gems(self, gems, board):
        assert (gems is not None)

        all_gems = board.get_gems()
        if ( greater_than_or_equal_to(all_gems, gems) ):
            # take the gems from the board
            board.take_gems(gems)

            # add to player's pocket
            self._add_gems(gems)

        else:
            raise ValueError(
                'Invalid gems counts! You want to get: {want}, but the Board only has: {existing}'.format(
                    want='\n'.join([f"{k}:{v}" for k, v in gems.items()]),
                    existing='\n'.join([f"{k}:{v}" for k, v in all_gems.items()])
                )
            )


    def pick_same_gems(self, gems, card, board):
        self.pick_gems(gems, board)


    def pick_different_gems(self, gems, card, board):
        self.pick_gems(gems, board)

    
    def buy_board_card(self, gems, card, board):
        assert (card is not None)

        if not self.can_afford(card):
            raise ValueError(
                f"Trying to buy a card with required gems {card.cost}, gems at hand: {self.gems_from_hand}; gems from card: {self.gems_from_card}"
            )

        all_cards = board.get_cards()
        all_cards_set = set(functools.reduce(operator.iconcat, all_cards, []))
        assert (card in all_cards_set), (
            f"Try to buy a card {card.id} that is not on the current board! "
        )

        # add up the reputation if any:
        self.rep += card.reputation

        # add the card to your pocket
        assert (card not in self.cards)
        self.cards.add(card)

        # update your card pocket map:
        self.gems_from_card[card.gem] += 1

        # substract your gem:
        diff_gems = self.update_gems(card.cost)

        board.take_card(card.id)
        board.payback_gems(diff_gems)
    
    def buy_reserve_card(self, gems, card, board):
        assert (card is not None)

        if not self.can_afford(card):
            raise ValueError(
                f"Trying to buy a card with required gems {card.cost}, gems at hand: {self.gems_from_hand}; gems from card: {self.gems_from_card}"
            )

        assert (card in self.rev_cards), (
            f"Try to buy a reserved card {card.id} that is not being reverved!"
        )

        # add the card to your pocket
        assert (card not in self.cards)
        self.cards.add(card)

        # update your card pocket map:
        self.gems_from_card[card.gem] += 1

        # substract your gem:
        diff_gems = self.update_gems(card.cost)

        # put the gems back to board
        board.payback_gems(diff_gems)

        # remove the reversed card:
        self.rev_cards.remove(card)
        self.reserve_count -= 1

    
    def reserve_card(self, gems, card, board):
        if self.reserve_count >= 3:
            raise ValueError("You cannot reserve the card because you have only reserved for three times!")

        all_cards = board.get_cards()
        all_cards_set = set(functools.reduce(operator.iconcat, all_cards, []))

        assert (card in all_cards_set), (
            f"Try to reserve a card {card.id} that is not in the board!"
        )

        assert (card not in self.rev_cards), (
            f"Try to reverse card: {card.id}, but you already have it!"
        )

        self.rev_cards.add(card)
        self.gems_from_hand[Gem.GOLD] += 1

        board.take_gems({Gem.GOLD: 1})
        board.take_card(card.id)
        self.reserve_count += 1


    def no_action(self, gems, card, board):
        pass

    
    # substract your gem, expect to update your current gems
    def update_gems(self, gem_cost):
        def _raise_not_enough_error():
            raise ValueError(
                'Not enough gem balance even you are using gold\n' +
                'You need: {}\n'.format('\n'.join(f'{k}:{v}' for k, v in gem_cost.items())) +
                'But you have: {}\n'.format('\n'.join(f'{k}:{v}' for k, v in self.gems_from_hand.items())) +
                'And your card value: {}\n'.format('\n'.join(f'{k}:{v}' for k, v in self.gems_from_card.items()))
            )

        gems_to_pay = {}
        for g, v in gem_cost.items():
            gem_in_hand = self.gems_from_hand.get(g, 0)
            gem_from_card = self.gems_from_card.get(g, 0)

            if (gem_in_hand + gem_from_card < v):
                gold_count = self.gems_from_hand.get(Gem.GOLD, 0)
                if (gem_in_hand + gem_from_card + gold_count >= v):
                    # substract the permanent gem:
                    remain = v - gem_from_card
                    if (remain > gem_in_hand):
                        # you will have to use gold here
                        self.gems_from_hand[g] = 0
                        self.gems_from_hand[Gem.GOLD] -= remain - gem_in_hand
                        assert (self.gems_from_hand[Gem.GOLD] >= 0)
                        gems_to_pay[Gem.GOLD] = remain - gem_in_hand
                        gems_to_pay[g] = gem_in_hand
                    else:
                        _raise_not_enough_error()
                        #self.gems_from_hand[g] -= gem_in_hand - remain
                        #gems_to_pay[g] = remain
                else:
                    _raise_not_enough_error()
            else:
                # pay without gold
                remain = v - gem_from_card
                # if remain <= 0, then you do not need to pay any thing!
                if (remain > 0):
                    # you still need to pay your gem
                    self.gems_from_hand[g] -= remain
                    assert(self.gems_from_hand[g] >= 0)
                    gems_to_pay[g] = remain 

        return gems_to_pay


    # your strategy will being called here:
    def take_action(self, board):
        # your strategy, you need to provide:
        # 1. action type
        # 2. params:
        #   - # gems you want to pick
        #   - Or: the card you want to buy or reserve

        action_params = self.strategy.next_step()
        action, gems, card_id = action_params.action, action_params.gems, action_params.card_id 
        card = board.get_card(card_id)
        self._func_map[action](gems, card, board)
        #pass


    # this is use to take an action from outside (for test)
    def take_external_action(self, action_params, board):
        action, gems, card_id = action_params.action, action_params.gems, action_params.card_id 
        card = board.get_card(card_id)
        self._func_map[action](gems, card, board)