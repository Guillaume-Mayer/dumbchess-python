import chess

#g = chess.Game(white = chess.HUMAN, black = chess.HUMAN)
#g = chess.Game(white = chess.COMPUTER, black = chess.COMPUTER)
g = chess.Game(white = chess.HUMAN, black = chess.COMPUTER)

g.start()

#import cProfile
#p = g.position
#cProfile.run("p.get_best_move_negamax(2)", "negamax.prof")

