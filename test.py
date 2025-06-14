from collections import defaultdict

from game import Game, GameState
from player_algo import MoveType, PlayerAlgo

player_algo = PlayerAlgo()
won = 0
lost = defaultdict(int)
total_games = 10000
for i in range(1, total_games + 1):
    game = Game()
    while game.state == GameState.UNSTARTED or game.state == GameState.IN_PROGRESS:
        player_algo.make_a_move(game=game)
    if game.state == GameState.WON:
        won += 1
        print(f"Game {i} WON")
    else:
        lost[player_algo.last_move_played] += 1
        print(f"Game {i} LOST")

print(f"Total Game {total_games} WON {won} WIN RATE {won / float(total_games)}")
print("LOST STATS:")
print(f"simple:{lost[MoveType.simple]}")
print(f"advanced:{lost[MoveType.advanced]}")
print(f"random:{lost[MoveType.random]}")
