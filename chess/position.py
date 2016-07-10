from .const import *
from .piece import *
from .move import *

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

# Position class
class Position:

    def start(self):
        """Initialize to regular start position"""
        self.color_to_play = WHITE
        # Castling flags
        self.can_castle_kingside    = [True, True]
        self.can_castle_queenside   = [True, True]
        # Last move two-push pawn move column
        self.two_push_col = -1
        # The position is a list of rows
        # a row is a list of pieces
        # Define first row (white pieces)
        row0 = [
            Rook(WHITE),
            Knight(WHITE),
            Bishop(WHITE),
            Queen(WHITE),
            King(WHITE),
            Bishop(WHITE),
            Knight(WHITE),
            Rook(WHITE),
        ]
        # Define second row (white pawns)
        row1 = []
        for c in range(8):
            row1.append(Pawn(WHITE))
        # Define seventh row (black pawns)
        row6 = []
        for c in range(8):
            row6.append(Pawn(BLACK))
        # Define last row (black pieces)
        row7 = [
            Rook(BLACK),
            Knight(BLACK),
            Bishop(BLACK),
            Queen(BLACK),
            King(BLACK),
            Bishop(BLACK),
            Knight(BLACK),
            Rook(BLACK),
        ]
        self.tiles = [
            row0,
            row1,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            row6,
            row7,
        ]
        # King position
        self.king_row = [7, 0]
        self.king_col = [4, 4]

    def __str__(self):
        s = "\n"
        for row in range(7, -1, -1):
            for col in range(8):
                if self.tiles[row][col] is None:
                    s += "-"
                else:
                    s += self.tiles[row][col].short_str()
            s += "\n"
        s += "\n" + COLOR_NAMES[self.color_to_play] + " to play"
        #if self.is_check(self.color_to_play):
        #    s += " (Check!)"
        s += "\n"
        return s

    def __eq__(self, other):
        if self.tiles != other.tiles: return False
        if self.color_to_play != other.color_to_play: return False
        if self.can_castle_queenside != other.can_castle_queenside: return False
        if self.can_castle_kingside != other.can_castle_kingside: return False
        if self.two_push_col != other.two_push_col: return False
        return True

    def key(self):
        # Not used
        # This tuple could serve as a dictionnary key
        tup = (self.color_to_play, tuple(self.can_castle_queenside), tuple(self.can_castle_kingside), self.two_push_col)
        tup += tuple(tuple(row) for row in self.tiles)
        return tup

    def play(self, move):
        """
        Play a move
        """
        assert self.tiles[move.row1][move.col1].color == self.color_to_play
        # Fill end tile
        self.tiles[move.row2][move.col2] = self.tiles[move.row1][move.col1]
        # Empty start tile
        self.tiles[move.row1][move.col1] = None
        # En Passant
        if move.en_passant:
            if self.color_to_play == WHITE:
                self.tiles[move.row2 - 1][move.col2] = None
            else:
                self.tiles[move.row2 + 1][move.col2] = None
        # Promotion
        elif move.promote:
            self.tiles[move.row2][move.col2] = self.tiles[move.row2][move.col2].promote(move.promote)
        # Castling
        elif move.castling is not None:
            if move.castling == KING:
                # Move king-side rook
                self.tiles[move.row1][5], self.tiles[move.row1][7] = self.tiles[move.row1][7], self.tiles[move.row1][5]
            elif move.castling == QUEEN:
                # Move queen-side rook
                self.tiles[move.row1][0], self.tiles[move.row1][3] = self.tiles[move.row1][3], self.tiles[move.row1][0]
        # Special moves stuff
        if self.two_push_col >= 0:
            # Store two push col in mmove so this can be restore on unplay
            move.two_push_col_was = self.two_push_col
            self.two_push_col = -1
        if move.piece == PAWN:
            if abs(move.row1 - move.row2) == 2:
                # Means that next move may be "en passant"
                self.two_push_col = move.col1
        elif move.piece == ROOK:
            if move.col1 == 0 and self.can_castle_queenside[self.color_to_play]:
                # Moving this rook makes queen-side castling impossible
                self.can_castle_queenside[self.color_to_play] = False
                move.prevents_castle_queenside = True
            elif move.col1 == 7 and self.can_castle_kingside[self.color_to_play]:
                # Moving this rook makes king-side castling impossible
                self.can_castle_kingside[self.color_to_play] = False
                move.prevents_castle_kingside = True
        elif move.piece == KING:
            # Keep track of kings positions (see is_check)
            self.king_row[self.color_to_play] = move.row2
            self.king_col[self.color_to_play] = move.col2
            if move.col1 == 4:
                # Moving the king makes castling impossible both sides
                if self.can_castle_kingside[self.color_to_play]:
                    self.can_castle_kingside[self.color_to_play] = False
                    move.prevents_castle_kingside = True
                if self.can_castle_queenside[self.color_to_play]:
                    self.can_castle_queenside[self.color_to_play] = False
                    move.prevents_castle_queenside = True
        # Swap color to play 
        self.color_to_play = (1 - self.color_to_play)

    def unplay(self, move):
        """
        Unplay a move
        """
        assert self.tiles[move.row2][move.col2].color == (1 - self.color_to_play)
        # Fill start tile
        self.tiles[move.row1][move.col1] = self.tiles[move.row2][move.col2]
        # Empty or fill end tile
        if move.capture is None or move.en_passant:
            self.tiles[move.row2][move.col2] = None
        else:
            self.tiles[move.row2][move.col2] = Piece.get_instance(self.color_to_play, move.capture)
        # En Passant
        if move.en_passant:
            if self.color_to_play == WHITE:
                self.tiles[move.row2 + 1][move.col2] = Pawn(self.color_to_play)
            else:
                self.tiles[move.row2 - 1][move.col2] = Pawn(self.color_to_play)
        # Promotion
        elif move.promote:
            self.tiles[move.row1][move.col1] = Pawn(1 - self.color_to_play)
        # Castling
        elif move.castling is not None:
            if move.castling == KING:
                # Move king-side rook
                self.tiles[move.row1][5], self.tiles[move.row1][7] = self.tiles[move.row1][7], self.tiles[move.row1][5]
            elif move.castling == QUEEN:
                # Move queen-side rook
                self.tiles[move.row1][0], self.tiles[move.row1][3] = self.tiles[move.row1][3], self.tiles[move.row1][0]
        # Swap color to play 
        self.color_to_play = (1 - self.color_to_play)
        # Special moves stuff
        self.two_push_col = move.two_push_col_was
        if move.prevents_castle_queenside:
            assert not self.can_castle_queenside[self.color_to_play]
            self.can_castle_queenside[self.color_to_play] = True
        if move.prevents_castle_kingside:
            assert not self.can_castle_kingside[self.color_to_play]
            self.can_castle_kingside[self.color_to_play] = True
        if move.piece == KING:
            self.king_row[self.color_to_play] = move.row1
            self.king_col[self.color_to_play] = move.col1          

    def resolve_move(self, move):
        # If row1 and col1 are filled move is considered resolved
        if move.row1 is not None and move.col1 is not None: return True
        # Move need to be resolved
        matching_moves = []
        moves = self.get_pseudo_legal_moves(self.color_to_play)
        for m in moves:
            if m.piece == move.piece and m.row2 == move.row2 and m.col2 == move.col2 and m.promote == move.promote:
                matching_moves.append(m)
        length = len(matching_moves)
        if length == 0:
            print("Move {} could not be resolved".format(move))
            return False
        elif length == 1:
            move.fill(matching_moves[0])
            return True
        elif length > 1:
            print("Move {} could not be resolved\nVarious match:".format(move))
            for m in matching_moves:
                print(m)
            return False        
    
    def check_move(self, move):
        moves = self.get_legal_moves(self.color_to_play)
        try:
            index = moves.index(move)
            move = moves[index]
            return True
        except ValueError:
            return False

    def get_legal_moves(self, color):
        # Get possible moves from each tile without considering check situation
        moves = self.get_pseudo_legal_moves(color)
        # Redo a list with only the moves that do not lead to check situation
        legal_moves = []
        for m in moves:
            self.play(m)
            if not self.is_check(color): legal_moves.append(m)
            self.unplay(m)
        return legal_moves
    
    def get_pseudo_legal_moves(self, color):
        # Get possible moves from each tile without considering check situation
        moves = []
        for row in range(8):
            for col in range(8):
                moves += self.get_moves_for_tile(row, col, color)
        return moves

    def get_moves_for_tile(self, row, col, color):
        # Assertions
        assert row in range(8)
        assert col in range(8)
        # No moves for empty tile
        if self.tiles[row][col] is None:
            return []
        # Get the piece
        piece = self.tiles[row][col]
        # Check the color
        if piece.color != color:
            return []
        # It now depends of the piece type
        if piece.piece == PAWN:
            return self.get_moves_for_pawn(row, col, color)
        elif piece.piece == ROOK:
            return self.get_moves_for_rook(row, col, color)
        elif piece.piece == BISHOP:
            return self.get_moves_for_bishop(row, col, color)
        elif piece.piece == KNIGHT:
            return self.get_moves_for_knight(row, col, color)
        elif piece.piece == KING:
            return self.get_moves_for_king(row, col, color)
        elif piece.piece == QUEEN:
            return self.get_moves_for_queen(row, col, color)

    def get_moves_for_king(self, row, col, color):
        moves = []
        for d in KING_MOVES:
            if self.is_empty_tile(row + d[0], col + d[1]):
                moves.append(Move(KING, row + d[0], col + d[1], row, col))
            elif self.is_capturable_tile(row + d[0], col + d[1], color):
                moves.append(Move(KING, row + d[0], col + d[1], row, col, self._capture))
        # Castling
        if self.can_castle_kingside[color]:
            # King-side castling
            if self.tiles[row][5] is None and self.tiles[row][6] is None:
                if self.tiles[row][7] is not None and self.tiles[row][7].piece == ROOK and self.tiles[row][7].color == color:
                    if (not self.is_tile_attacked(row, 5, color) and not self.is_tile_attacked(row, 6, color)):
                        moves.append(Move(KING, row, 6, row, 4, castling = KING))
        if self.can_castle_queenside[color]:
            # Queen-side castling
            if self.tiles[row][3] is None and self.tiles[row][2] is None and self.tiles[row][1] is None:
                if self.tiles[row][0] is not None and self.tiles[row][0].piece == ROOK and self.tiles[row][0].color == color:
                    if (not self.is_tile_attacked(row, 3, color) and not self.is_tile_attacked(row, 2, color)):
                        moves.append(Move(KING, row, 2, row, 4, castling = QUEEN))
        return moves

    def get_moves_for_queen(self, row, col, color):
        return self.get_moves_for_rook(row, col, color, QUEEN) + self.get_moves_for_bishop(row, col, color, QUEEN)

    def get_moves_for_rook(self, row, col, color, piece = ROOK):
        moves = []
        # To the left
        for c in range(col - 1, -1, -1):
            if self.tiles[row][c] is None:
                moves.append(Move(piece, row, c, row, col))
            elif self.is_capturable_tile(row, c, color):
                moves.append(Move(piece, row, c, row, col, self._capture))
                break
            else:
                break
        # To the right
        for c in range(col + 1, 8, +1):
            if self.tiles[row][c] is None:
                moves.append(Move(piece, row, c, row, col))
            elif self.is_capturable_tile(row, c, color):
                moves.append(Move(piece, row, c, row, col, self._capture))
                break
            else:
                break
        # To the top
        for r in range(row + 1, 8, +1):
            if self.tiles[r][col] is None:
                moves.append(Move(piece, r, col, row, col))
            elif self.is_capturable_tile(r, col, color):
                moves.append(Move(piece, r, col, row, col, self._capture))
                break
            else:
                break
        # To the bottom
        for r in range(row - 1, -1, -1):
            if self.tiles[r][col] is None:
                moves.append(Move(piece, r, col, row, col))
            elif self.is_capturable_tile(r, col, color):
                moves.append(Move(piece, r, col, row, col, self._capture))
                break
            else:
                break
        return moves

    def get_moves_for_bishop(self, row, col, color, piece = BISHOP):
        moves = []
        # To Top-Right
        r, c = row + 1, col + 1
        while r < 8 and c < 8:
            if self.tiles[r][c] is None:
                moves.append(Move(piece, r, c, row, col))
            elif self.is_capturable_tile(r, c, color):
                moves.append(Move(piece, r, c, row, col, self._capture))
                break
            else:
                break
            r, c = r + 1, c + 1
        # To Top-Left
        r, c = row + 1, col - 1
        while r < 8 and c >= 0:
            if self.tiles[r][c] is None:
                moves.append(Move(piece, r, c, row, col))
            elif self.is_capturable_tile(r, c, color):
                moves.append(Move(piece, r, c, row, col, self._capture))
                break
            else:
                break
            r, c = r + 1, c - 1
        # To Bottom-Left
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0:
            if self.tiles[r][c] is None:
                moves.append(Move(piece, r, c, row, col))
            elif self.is_capturable_tile(r, c, color):
                moves.append(Move(piece, r, c, row, col, self._capture))
                break
            else:
                break
            r, c = r - 1, c - 1
        # To Bottom-Right
        r, c = row - 1, col + 1
        while r >= 0 and c < 8:
            if self.tiles[r][c] is None:
                moves.append(Move(piece, r, c, row, col))
            elif self.is_capturable_tile(r, c, color):
                moves.append(Move(piece, r, c, row, col, self._capture))
                break
            else:
                break
            r, c = r - 1, c + 1
        return moves

    def get_moves_for_knight(self, row, col, color):
        moves = []
        for d in KNIGHT_MOVES:
            if self.is_empty_tile(row + d[0], col + d[1]):
                moves.append(Move(KNIGHT, row + d[0], col + d[1], row, col))
            elif self.is_capturable_tile(row + d[0], col + d[1], color):
                moves.append(Move(KNIGHT, row + d[0], col + d[1], row, col, self._capture))
        return moves

    def get_moves_for_pawn(self, row, col, color):
        if color == WHITE:
            sens = +1
            init_row = (row == 1)
            prom_row = (row == 6)
            ep_row = (row == 4)
        else:
            sens = -1
            init_row = (row == 6)
            prom_row = (row == 1)
            ep_row = (row == 3)
        moves = []
        # Move one tile
        if self.tiles[row + sens][col] is None:
            moves.append(Move(PAWN, row + sens, col, row, col))
            # Move two tiles
            if init_row and self.tiles[row + 2*sens][col] is None:
                moves.append(Move(PAWN, row + 2*sens, col, row, col))
        # Capture on left
        if self.is_capturable_tile(row + sens, col - 1, color):
            moves.append(Move(PAWN, row + sens, col - 1, row, col, self._capture))
        elif ep_row and col > 0 and self.two_push_col == col - 1:
            # Capture en passant
            moves.append(Move(PAWN, row + sens, col - 1, row, col, PAWN, en_passant = True))
        # Capture on right
        if self.is_capturable_tile(row + sens, col + 1, color):
            moves.append(Move(PAWN, row + sens, col + 1, row, col, self._capture))
        elif ep_row and col < 7 and self.two_push_col == col + 1:
            # Capture en passant
            moves.append(Move(PAWN, row + sens, col + 1, row, col, PAWN, en_passant = True))
        # Promotion
        if prom_row and moves: 
            promotions = (QUEEN, KNIGHT, ROOK, BISHOP)
            p_moves = []
            for m in moves:
                for p in promotions:
                    p_m = m.copy()
                    p_m.promote = p
                    p_moves.append(p_m)
            return p_moves
        return moves

    def is_empty_tile(self, row, col):
        if row < 0: return False
        if col < 0: return False
        if row > 7: return False
        if col > 7: return False
        return self.tiles[row][col] is None

    def is_capturable_tile(self, row, col, color):
        if row < 0: return False
        if col < 0: return False
        if row > 7: return False
        if col > 7: return False
        piece = self.tiles[row][col]
        if piece is None: return False
        if piece.color == color: return False
        if piece.piece == KING: return False
        # Store the captured piece to store in move
        self._capture = piece.piece
        return True

    # Optimized version for is_tile_attacked
    def is_capturable_tile_o(self, row, col, color):
        if self.tiles[row][col].color == color: return False
        self._capture = self.tiles[row][col].piece
        return True
        
    def is_tile_attacked(self, row, col, color):
        # Check bishop style attacks (including bishop, pawn, king and queen)
        # - On top-right
        r, c = row + 1, col + 1
        while r < 8 and c < 8:
            if self.tiles[r][c] is None:
                pass
            elif self.is_capturable_tile_o(r, c, color):
                if self._capture == BISHOP:
                    return True
                elif self._capture == PAWN:
                    if r == row + 1 and color == WHITE: return True
                elif self._capture == KING:
                    if r == row + 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
            r, c = r + 1, c + 1     
        # - On top-left
        r, c = row + 1, col - 1
        while r < 8 and c >= 0:
            if self.tiles[r][c] is None:
                pass
            elif self.is_capturable_tile_o(r, c, color):
                if self._capture == BISHOP:
                    return True
                elif self._capture == PAWN:
                    if r == row + 1 and color == WHITE: return True
                elif self._capture == KING:
                    if r == row + 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
            r, c = r + 1, c - 1     
        # - On bottom-left
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0:
            if self.tiles[r][c] is None:
                pass
            elif self.is_capturable_tile_o(r, c, color):
                if self._capture == BISHOP:
                    return True
                elif self._capture == PAWN:
                    if r == row - 1 and color == BLACK: return True
                elif self._capture == KING:
                    if r == row - 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
            r, c = r - 1, c - 1     
        # - On bottom-right
        r, c = row - 1, col + 1
        while r >= 0 and c < 8:
            if self.tiles[r][c] is None:
                pass
            elif self.is_capturable_tile_o(r, c, color):
                if self._capture == BISHOP:
                    return True
                elif self._capture == PAWN:
                    if r == row - 1 and color == BLACK: return True
                elif self._capture == KING:
                    if r == row - 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
            r, c = r - 1, c + 1     
        # Check rook style attacks (including rook, king and queen)
        # - On left
        for c in range(col - 1, -1, -1):
            if self.tiles[row][c] is None:
                pass
            elif self.is_capturable_tile_o(row, c, color):
                if self._capture == ROOK:
                    return True
                elif self._capture == KING:
                    if c == col - 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
        # - On right
        for c in range(col + 1, 8):
            if self.tiles[row][c] is None:
                pass
            elif self.is_capturable_tile_o(row, c, color):
                if self._capture == ROOK:
                    return True
                elif self._capture == KING:
                    if c == col + 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
        # - On top
        for r in range(row + 1, 8):
            if self.tiles[r][col] is None:
                pass
            elif self.is_capturable_tile_o(r, col, color):
                if self._capture == ROOK:
                    return True
                elif self._capture == KING:
                    if r == row + 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
        # - On bottom
        for r in range(row - 1, -1, -1):
            if self.tiles[r][col] is None:
                pass
            elif self.is_capturable_tile_o(r, col, color):
                if self._capture == ROOK:
                    return True
                elif self._capture == KING:
                    if r == row - 1: return True
                elif self._capture == QUEEN:
                    return True
                break
            else:
                break
        # Check knight attack
        for d in KNIGHT_MOVES:
            if self.is_capturable_tile(row + d[0], col + d[1], color):
                if self._capture == KNIGHT:
                    return True
        # Not attacked then
        return False
    
    def is_check(self, color):
        assert self.tiles[self.king_row[color]][self.king_col[color]].piece == KING
        assert self.tiles[self.king_row[color]][self.king_col[color]].color == color
        return self.is_tile_attacked(self.king_row[color], self.king_col[color], color)

    def get_material_value(self):
        material = [0, 0]
        for row in range(8):
            for col in range(8):
                if self.tiles[row][col] is not None:
                    material[self.tiles[row][col].color] += self.tiles[row][col].get_material_value()
        return material[self.color_to_play] - material[1 - self.color_to_play]

    def eval(self, coef_t = 1, coef_m = 1):
        """
        coef_t = Coef for tactical score (mobility)
        coef_m = Coef for material score (material value)
        """
        mobility = len(self.get_legal_moves(self.color_to_play))
        # Mate situations
        if mobility == 0:
            if self.is_check(self.color_to_play):
                return -MATE
            else:
                return DRAW
        # Get adversary mobility by temporarily swapping color
        temp = self.color_to_play
        self.color_to_play = 1 - temp
        mobility -= len(self.get_legal_moves(self.color_to_play))
        self.color_to_play = temp
        # Evaluate position according to coefs
        return (mobility * coef_t) + (self.get_material_value() * coef_m)
        
    def get_best_move(self):
        return self.get_best_move_negamax(3)
        
    def get_best_move_negamax(self, depth):
        score, move = self.negamax(depth, -INFINITY, +INFINITY)
        print("Negamax({}): {} [{}]".format(depth, score, ", ".join([str(m) for m in move])))
        if move: return move[0]

    def negamax(self, depth, alpha, beta):
        """
        See Negamax with alpha beta pruning
        on https://en.wikipedia.org/wiki/Negamax
        """
        if depth == 0:
            return self.eval(), ()
        moves = self.get_legal_moves(self.color_to_play)
        if len(moves) == 0:
            return self.eval(), ()
        best_score, best_move = -INFINITY, ()
        for m in moves:
            self.play(m)
            score, move_tuple = self.negamax(depth - 1, -beta, -alpha)
            score *= -1
            self.unplay(m)
            if score > best_score:
                best_score = score
                best_move = (m,) + move_tuple
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return best_score, best_move


