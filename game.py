#! /usr/local/bin/python3

import time
import sys
from board import Board


class Game(object):
    def __init__(self, players_cnt):
        self.board = Board(players_cnt, should_shuffle=True)
    
    def play(self):
        can_win = False
        while not can_win:
            # take turns
            for player in self.board.players:
                player.take_action(self.board)
                self.board._check_and_update_nobles(player)
                if player.can_win(self.board.points_to_win):
                    can_win = True
        winners = []
        if can_win:
            winners = [p.id for p in self.board._get_winners()]
        return winners

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        print("Missing arguments: python3 game.py player_cnt rounds")
        exit(1)

    players = int(args[0])
    rounds = int(args[1])
    win = {}
    even = {}
    for i in range(players):
        win[i] = 0
        even[i] = 0
    
    start = time.perf_counter()
    for i in range(rounds):
        game = Game(players)
        winners = game.play()
        if len(winners) == 1:
            win[winners[0]] = win[winners[0]] + 1
        else:
            for w in winners:
                even[w] = even[w] + 1
    end = time.perf_counter()
    print(f"Time spent: {end - start:0.4f} seconds")
    for i in range(players):
        print(f"Player {i} win rate: {win[i] / rounds:.2%}, even rate: {even[i] / rounds:.2%}")