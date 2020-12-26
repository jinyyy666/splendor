import functools
import itertools
import operator
import collections

from enum import Enum
from board import (
    Gem,
    Card,
    Noble,
)
from util import (
    can_get_gem
)


REPUTATION_TO_WIN = 15

class Action(Enum):
    PICK_THREE = 0
    PICK_SAME = 1
    BUY_CARD = 2
    RESERVE_CARD = 3
    BUY_RESERVE_CARD = 4
    NONE = 5

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
        self.rev_cards = {}

        # number of gold:
        self.gold = 0

        # the gems player has via the develop card
        self.gems_from_card = {
            gem: 0 for gem in Gem.__members__.keys()
        }

        # the gems player has in hand
        self.gems_from_hand = {
            gem: 0 for gem in Gem.__members__.keys()
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


    def can_win(self):
        return self.rep >= REPUTATION_TO_WIN


    def can_afford(self, card):
        c_dict = collections.defaultdict(int)
        for k, v in itertools.chain(self.gems_from_card.items(), self.gems_from_hand.items()):
            c_dict[k] += v
        total_available_gems = dict(c_dict)

        gold_count = self.gems_from_hand[Gem.GOLD]
        for gem_t, cnt in card.cost.items():
            availb = total_available_gems[gem_t]
            if cnt > availb:
                if cnt + gold_count > availb:
                    return False
                else:
                    gold_count = gold_count - (cnt - availb)
                    assert (gold_count >= 0)
        return True


    def get_id(self):
        return self.id

    def _add_gems(self, gems):
        for gem_t, cnt in gems.items:
            self.gems_from_hand[gem_t] += cnt


    def card_summary(self):
        summary = {}
        for c in self.cards:
            if c.gem not in summary:
                summary[c.gem] = 0
            summary[c.gem] += 1
        return summary
        

    # ---------------------------------------------------------
    # Here are all the standard operations the player can take
    # 1. pick three different gems
    # 2. pick two gems if there are 4 gems given a kind
    # 3. buy a development card
    # 4. reserve a development card and get a gold
    # ---------------------------------------------------------
    def pick_gems(self, gems, board):
        all_gems = board.get_gems()
        if ( can_get_gem(all_gems, gems) ):
            # take the gems from the board
            board.take_gems(gems)

            # add to player's pocket
            self._add_gems(gems)

        else:
            raise ValueError(
                'Invalid gems counts! You want to get: {want}, but the Board only has: {existing}'.format(
                    want='\n'.join([str(k) + ":" + v for k, v in gems]),
                    existing='\n'.join([str(k) + ":" + v for k, v in all_gems])
                )
            )


    def pick_same_gems(self, gems, card, board):
        self.pick_gems(gems, board)


    def pick_different_gems(self, gems, card, board):
        self.pick_gems(gems, board)

    
    def buy_board_card(self, gems, card, board):
        if not self.can_afford(card):
            raise ValueError(
                f"Trying to buy a card with required gems {card.cost}, gems at hand: {self.gems_from_hand}; gems from card: {self.gems_from_card}"
            )
        
        all_cards = board.get_cards()
        all_cards_set = set(functools.reduce(operator.iconcat, all_cards.values(), []))
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
        self.update_gems(card.cost)

        board.take_card(card.id)

    
    def buy_reserve_card(self, gems, card, board):
        if not self.can_afford(card):
            raise ValueError(
                f"Trying to buy a card with required gems {card.cost}, gems at hand: {self.}; gems from card: {self.gems_from_card}"
            )

        assert (card in self.rev_cards), (
            "Try to buy a reserved card {i} that is not being reverved!".format(
                i=card.id if card else -1
            )
        )

        # add the card to your pocket
        assert (card not in self.cards)
        self.cards.add(card)

        # update your card pocket map:
        self.gems_from_card[card.gem] += 1

        # substract your gem:
        self.update_gems(card.cost)

        # remove the reversed card:
        self.rev_cards.remove(card)
        self.reserve_count -= 1

    
    def reserve_card(self, gems, card, board):
        if self.reserve_count >= 3:
            raise ValueError("You cannot reserve the card because you have only reserved for three times!")

        all_cards = board.get_cards()

        assert (card in all_cards), (
            "Try to reserve a card {i} that is not in the board!".format(
                i=card.id if card else -1
            )
        )

        self.rev_cards.add(card)
        self.gems_from_hand[Gem.GOLD] += 1

        board.take_card(card.id)
        self.reserve_count += 1
        

    def no_action(self, gems, card, board):
        pass

    
    # substract your gem, expect to update your current gems
    def update_gems(self, gem_cost):
        for g, v in gem_cost.items():
            gem_in_hand = self.gems_from_hand[g] if g in gems else 0
            gem_from_card = self.gems_from_card[g]

            if (gem_in_hand + gem_from_card < v):
                gold_count = self.gems_from_hand[Gem.GOLD] if self.gems_from_hand[Gem.GOLD] > 0 else 0
                if (gem_in_hand + gem_from_card + gold_count >= v):
                    # substract the permanent gem:
                    remain = v - gem_from_card
                    if (remain > gem_in_hand):
                        # you will have to use gold here
                        self.gems_from_hand[g] = 0
                        self.gems_from_hand[Gem.GOLD] -= remain - gem_in_hand
                        assert (self.gems_from_hand[Gem.GOLD] >= 0)
                    else:
                        # you do not need to use gold:
                        self.gems_from_hand[g] -= gem_in_hand - remain
                else:
                    raise ValueError(
                        'Not enough gem balance even you are using gold\n' +
                        'You need: {}\n'.format('\n'.join(str(k) + ':' + v for k, v in gem_cost.items())) +
                        'But you have: {}'.format('\n'.join(str(k) + ':' + v for k, v in self.gems_from_hand.items())) +
                        'And your card value: {}'.format('\n'.join(str(k) + ':' + v for k, v in self.gems_from_card.items()))
                    )
            else:
                remain = v - gem_from_card
                # if remain <= 0, then you do not need to pay any thing!
                if (remain > 0):
                    # you still need to pay your gem
                    self.gems_from_hand[g] -= remain
                    assert(self.gems_from_hand[g] >= 0)

    
    # your strategy will being called here:
    def take_action(self, board):
        # your strategy, you need to provide:
        # 1. action type
        # 2. params:
        #   - # gems you want to pick 
        #   - Or: the card you want to buy or reserve
        (action, gems, card) = self.next_step(board)

        self._func_map[action](gems, card, board)

    # dummy at this moment:
    def next_step(self, board):
        return Action.NONE, None, None
    