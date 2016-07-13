# Piece constants
KING	= 0
QUEEN	= 1
ROOK	= 2
BISHOP	= 3
KNIGHT	= 4
PAWN	= 5

# Piece char for ascii representation
PIECE_SHORT	= "K", "Q", "R", "B", "N", "P"

# Piece code for algebric notation
PIECE_ALG	= "K", "Q", "R", "B", "N", ""

# Color constants
BLACK = 0
WHITE = 1

# Color names
COLOR_NAMES	= "Black", "White"

# Opponents constants
HUMAN		= 0
COMPUTER	= 1

# Evaluation constants
MATE		= 999999999
INFINITY	= (MATE + 1)
DRAW		= 0

# Move constants
KING_MOVES = (
    (-1, -1),
    (-1,  0),
    (-1, +1),
    ( 0, -1),
    ( 0, +1),
    (+1, -1),
    (+1,  0),
    (+1, +1)
)

KNIGHT_MOVES = (
    (-2, -1),
    (-2, +1),
    (-1, -2),
    (-1, +2),
    (+1, -2),
    (+1, +2),
    (+2, -1),
    (+2, +1)
)