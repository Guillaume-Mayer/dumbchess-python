import os
import datetime
import cProfile

import chess

# Initialize game
g = chess.Game()

# Get initial position
p = g.position

# Initialise e2-e4 move 
m = chess.move.Move(chess.const.PAWN, 3, 4, 1, 4)

# PLay and print
p.play(m)
print(p)

# Generate profile file
depth     = 5
now       = datetime.datetime.now()
file_name = "negamax{}_{:0>4}{:0>2}{:0>2}_{:0>2}{:0>2}{:0>2}.prof".format(depth, now.year, now.month, now.day, now.hour, now.minute, now.second)

cProfile.run("p.get_best_move_negamax({})".format(depth), file_name)

# Open snakeviz
os.system("snakeviz " + file_name)