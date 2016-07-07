import os
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

#dir(cProfile)
# Generate profile file
cProfile.run("p.get_best_move_negamax(4)", "negamax.prof")

# Open snakeviz
os.system("snakeviz negamax.prof")