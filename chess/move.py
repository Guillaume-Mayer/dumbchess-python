from .const import *

import re

# Move class
class Move:

    def __init__(   self, piece, row2, col2, row1 = None, col1 = None,
                    capture = None, check = False, promote = None,
                    en_passant = False, castling = None):
        # Assertions
        assert piece in range(6)
        assert row2 in range(8)
        assert col2 in range(8)
        assert row1 != row2 or col1 != col2
        assert not capture or capture in range(6)
        assert not promote or promote in (QUEEN, KNIGHT, ROOK, BISHOP)
        assert not castling or (piece == KING and row1 in (0,7) and row1 == row2 
            and col1 == 4 and col2 in (2, 6) and castling in (KING, QUEEN))
        # Assignments
        self.piece                     = piece
        self.row2                      = row2
        self.col2                      = col2
        self.row1                      = row1
        self.col1                      = col1
        self.capture                   = capture
        self.check                     = check
        self.promote                   = promote
        self.en_passant                = en_passant
        self.castling                  = castling
        self.prevents_castle_kingside  = False
        self.prevents_castle_queenside = False
        self.two_push_col_was          = -1

    def copy(self):
        """
        Copy a move
        Since this is done only when promoting a pawn some attributes are not copied
        See Position.get_moves_for_pawn
        """
        copy = Move(
            self.piece,
            self.row2,
            self.col2,
            self.row1,
            self.col1,
            self.capture,
            self.check
            )
        return copy

    def fill(self, other):
        # Used by Position.resolve_move
        self.piece      = other.piece
        self.row1       = other.row1
        self.col1       = other.col1
        self.capture    = other.capture
        self.check      = other.check
        self.promote    = other.promote
        self.en_passant = other.en_passant
        self.castling   = other.castling

    def __str__(self):
        # Castling
        if self.castling != None:
            if self.castling == KING:
                s = "O-O"
            elif self.castling == QUEEN:
                s = "O-O-O"
        else:
            # Piece
            s = PIECE_ALG[self.piece]
            # Start coords
            if self.col1 != None: s += "abcdefgh"[self.col1]
            if self.row1 != None: s += str(self.row1 + 1)
            # Move or eat
            if self.col1 != None or self.row1 != None:
                if self.capture != None:
                    s += "x"
                else:
                    s += "-"
            # End coords
            s += "abcdefgh"[self.col2]
            s += str(self.row2 + 1)
            # promote
            if self.promote:
                s += PIECE_ALG[self.promote]
            # en passant
            elif self.en_passant:
                s += "e.p."
        # Check
        if self.check:
            s += "+"
        return s

    def __eq__(self, other):
        if self.row1 != other.row1: return False
        if self.col1 != other.col1: return False
        if self.row2 != other.row2: return False
        if self.col2 != other.col2: return False
        if self.promote != other.promote: return False
        return True

    @staticmethod
    def parse(string):
        match = re.match(r"^(?P<piece>[KQRBN])?(?P<startorend>[a-h][1-8])([-x]?(?P<end>[a-h][1-8]))?(?P<prom>[QNRB])?(e\.p\.)?\+?$", string)
        if match:
            # Get piece
            if match.group("piece"):
                piece = "KQRBN".index(match.group("piece"))
            else:
                piece = PAWN
            # Get start and end tiles
            if match.group("end"):
                start = match.group("startorend")
                end = match.group("end")
                row1 = int(start[1]) - 1
                col1 = "abcdefgh".index(start[0])
                row2 = int(end[1]) - 1
                col2 = "abcdefgh".index(end[0])
            else:
                end = match.group("startorend")
                row1 = None
                col1 = None
                row2 = int(end[1]) - 1
                col2 = "abcdefgh".index(end[0])
            # Get promotion
            if match.group("prom"):
                prom = "KQRBN".index(match.group("prom"))
            else:
                prom = None
            # Instanciate Move
            m = Move(piece, row2, col2, row1, col1, promote = prom)
            return m
