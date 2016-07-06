from .const import *
from .piece import *
from .move import *

import random

# Position class
class Position:

	def start(self):
		"""Initialize to regular start position"""
		
		# White move first
		self.color_to_play = WHITE
		
		# Castling flags
		self.can_castle_kingside	= [True, True]
		self.can_castle_queenside	= [True, True]
		
		# Last move two-push pawn move column
		self.two_push_col = -1

		# the position is a list of rows
		# a row is a list of pieces
		# define first row (white pieces)
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
		# define second row (white pawns)
		row1 = []
		for c in range(8):
			row1.append(Pawn(WHITE))
		# define seventh row (black pawns)
		row6 = []
		for c in range(8):
			row6.append(Pawn(BLACK))
		# define last row (black pieces)
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

	def copy(self):
		# Return a copy of thh position
		copy = Position()
		# Copy flags
		copy.can_castle_kingside	= [self.can_castle_kingside[0], self.can_castle_kingside[1]] 
		copy.can_castle_queenside	= [self.can_castle_queenside[0], self.can_castle_queenside[1]]
		# Copy tiles
		copy.tiles = []
		for row in range(8):
			copy.tiles.append([])
			for col in range(8):
				copy.tiles[row].append(self.tiles[row][col])
		return copy

	def __str__(self):
		s = "\n"
		for row in range(7, -1, -1):
			for col in range(8):
				if self.tiles[row][col] == None:
					s += "-"
				else:
					s += self.tiles[row][col].short_str()
			s += "\n"
		s += "\n" + COLOR_NAMES[self.color_to_play] + " to play"
		s += "\n"
		return s

	def __add__(self, move):
		# Only a Move can be added to a position
		assert isinstance(move, Move)

		# Check start coords
		t1 = self.tiles[move.row1][move.col1]
		if t1 == None:
			raise BadMoveException("Start tile is empty")
		# Check piece
		if t1.piece != move.piece:
			raise BadMoveException("Piece does not match")
		# Check color to play
		if t1.color != self.color_to_play:
			raise BadMoveException(COLOR_NAMES[t1.color] + " cannot play")
		# Check end coords
		t2 = self.tiles[move.row2][move.col2]
		if t2:
			if t2.color == t1.color:
				raise BadMoveException("End tile is not empty")
		
		# Generate a new position
		new_pos = self.copy()
		# Fill end tile
		new_pos.tiles[move.row2][move.col2] = new_pos.tiles[move.row1][move.col1]
		# Empty start tile
		new_pos.tiles[move.row1][move.col1] = None
		# En Passant
		if move.en_passant:
			if self.color_to_play == WHITE:
				new_pos.tiles[move.row2 - 1][move.col2] = None
			else:
				new_pos.tiles[move.row2 + 1][move.col2] = None
		# Promotion
		elif move.promote:
			new_pos.tiles[move.row2][move.col2] = new_pos.tiles[move.row2][move.col2].promote(move.promote)
		# Castling
		elif move.castling != None:
			if move.castling == KING:
				# Move king-side rook
				new_pos.tiles[move.row1][5], new_pos.tiles[move.row1][7] = new_pos.tiles[move.row1][7], new_pos.tiles[move.row1][5]
			elif move.castling == QUEEN:
				# Move queen-side rook
				new_pos.tiles[move.row1][0], new_pos.tiles[move.row1][3] = new_pos.tiles[move.row1][3], new_pos.tiles[move.row1][0]
		# Update two-push and castling flags
		new_pos.two_push_col = -1
		if move.piece == PAWN:
			if abs(move.row1 - move.row2) == 2:
				new_pos.two_push_col = move.col1
		elif move.piece == ROOK:
			if move.col1 == 0:
				new_pos.can_castle_queenside[self.color_to_play] = False
			elif move.col1 == 7:
				new_pos.can_castle_kingside[self.color_to_play] = False
		elif move.piece == KING:
			if move.col1 == 4:
				new_pos.can_castle_kingside[self.color_to_play] = False
				new_pos.can_castle_queenside[self.color_to_play] = False
		# Swap color to play 
		new_pos.color_to_play = (1 - self.color_to_play)

		# Return new position
		return new_pos

	def __sub__(self, move):
		# Only a Move can be substracted from a position
		assert isinstance(move, Move)

		# Check end coords
		t2 = self.tiles[move.row2][move.col2]
		if t2 == None:
			raise BadMoveException("End tile is empty")
		# Check piece
		if t2.piece != move.piece:
			raise BadMoveException("Piece does not match")
		# Check color to play
		if t2.color == self.color_to_play:
			raise BadMoveException(COLOR_NAMES[t1.color] + " cannot unplay")
		# Check start coords
		t1 = self.tiles[move.row1][move.col1]
		if t1:
			raise BadMoveException("Start tile is not empty")
		
		# Generate a new position
		new_pos = self.copy()
		# Fill start tile
		new_pos.tiles[move.row1][move.col1] = new_pos.tiles[move.row2][move.col2]
		# Empty or fill end tile
		if move.capture == None or move.en_passant:
			new_pos.tiles[move.row2][move.col2] = None
		else:
			new_pos.tiles[move.row2][move.col2] = Piece.get_instance(self.color_to_play, move.capture)
		# En Passant
		if move.en_passant:
			if self.color_to_play == WHITE:
				new_pos.tiles[move.row2 + 1][move.col2] = Pawn(self.color_to_play)
			else:
				new_pos.tiles[move.row2 - 1][move.col2] = Pawn(self.color_to_play)
		# Promotion
		elif move.promote:
			new_pos.tiles[move.row1][move.col1] = Pawn(1 - self.color_to_play)
		# Castling
		elif move.castling != None:
			if move.castling == KING:
				# Move king-side rook
				new_pos.tiles[move.row1][5], new_pos.tiles[move.row1][7] = new_pos.tiles[move.row1][7], new_pos.tiles[move.row1][5]
			elif move.castling == QUEEN:
				# Move queen-side rook
				new_pos.tiles[move.row1][0], new_pos.tiles[move.row1][3] = new_pos.tiles[move.row1][3], new_pos.tiles[move.row1][0]
		# Update two-push and castling flags
		"""
		new_pos.two_push_col = -1
		if move.piece == KING:
			if move.col1 == 4:
				new_pos.can_castle_kingside[self.color_to_play] = False
				new_pos.can_castle_queenside[self.color_to_play] = False
		elif move.piece == ROOK:
			if move.col1 == 0:
				new_pos.can_castle_queenside[self.color_to_play] = False
			elif move.col1 == 7:
				new_pos.can_castle_kingside[self.color_to_play] = False
		elif move.piece == PAWN:
			if abs(move.row1 - move.row2) == 2:
				new_pos.two_push_col = move.col1
		"""
		# Swap color to play 
		new_pos.color_to_play = (1 - self.color_to_play)

		# Return new position
		return new_pos

	def resolve_move(self, move):
		# If row1 and col1 are filled move is considered resolved
		if move.row1 != None and move.col1 != None: return True
		# Move need to be resolved
		matching_moves = []
		moves = self.get_pseudo_legal_moves()
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
		moves = self.get_legal_moves()
		try:
			index = moves.index(move)
			move = moves[index]
			return True
		except ValueError:
			return False

	def get_legal_moves(self):
		# Get possible moves from each tile without considering check situation
		moves = self.get_pseudo_legal_moves()
		# Redo a list with only the moves that do not lead to check situation
		legal_moves = []
		for m in moves:
			new_pos = self + m
			new_pos._check = False
			new_pos.get_pseudo_legal_moves()
			if not new_pos._check:
				legal_moves.append(m)
		return legal_moves	

	def get_pseudo_legal_moves(self):
		# Get possible moves from each tile without considering check situation
		moves = []
		for row in range(8):
			for col in range(8):
				moves += self.get_moves_for_tile(row, col)
		return moves

	def get_moves_for_tile(self, row, col):
		# Assertions
		assert row in range(8)
		assert col in range(8)
		# No moves for empty tile
		if self.tiles[row][col] == None:
			return []
		# Get the piece
		piece = self.tiles[row][col]
		# Check the color
		if piece.color != self.color_to_play:
			return []
		# It now depends of the piece type
		if piece.piece == PAWN:
			return self.get_moves_for_pawn(row, col)
		elif piece.piece == ROOK:
			return self.get_moves_for_rook(row, col)
		elif piece.piece == BISHOP:
			return self.get_moves_for_bishop(row, col)
		elif piece.piece == KNIGHT:
			return self.get_moves_for_knight(row, col)
		elif piece.piece == KING:
			return self.get_moves_for_king(row, col)
		elif piece.piece == QUEEN:
			return self.get_moves_for_queen(row, col)

	def get_moves_for_king(self, row, col):
		moves = []
		delta = (
			(-1, -1),
			(-1,  0),
			(-1, +1),
			( 0, -1),
			( 0, +1),
			(+1, -1),
			(+1,  0),
			(+1, +1)
		)
		for d in delta:
			# Move
			if self.is_empty_tile(row + d[0], col + d[1]):
				moves.append(Move(KING, row + d[0], col + d[1], row, col))
			elif self.is_capturable_tile(row + d[0], col + d[1]):
				moves.append(Move(KING, row + d[0], col + d[1], row, col, self._capture))
		# Castling
		# WARNING Check rules when castling
		if self.can_castle_kingside[self.color_to_play]:
			# King-side castling
			if self.is_empty_tile(row, 5):
				if self.is_empty_tile(row, 6):
					moves.append(Move(KING, row, 6, row, 4, castling = KING))
		if self.can_castle_queenside[self.color_to_play]:
			# Queen-side castling
			if self.is_empty_tile(row, 3):
				if self.is_empty_tile(row, 2):
					if self.is_empty_tile(row, 1):
						moves.append(Move(KING, row, 2, row, 4, castling = QUEEN))
		return moves

	def get_moves_for_queen(self, row, col):
		moves = self.get_moves_for_rook(row, col, QUEEN)
		moves += self.get_moves_for_bishop(row, col, QUEEN)
		return moves

	def get_moves_for_rook(self, row, col, piece = ROOK):
		moves = []
		# To the left
		for c in range(col - 1, -1, -1):
			if self.is_empty_tile(row, c):
				moves.append(Move(piece, row, c, row, col))
			elif self.is_capturable_tile(row, c):
				moves.append(Move(piece, row, c, row, col, self._capture))
				break
			else:
				break
		# To the right
		for c in range(col + 1, 8, +1):
			if self.is_empty_tile(row, c):
				moves.append(Move(piece, row, c, row, col))
			elif self.is_capturable_tile(row, c):
				moves.append(Move(piece, row, c, row, col, self._capture))
				break
			else:
				break
		# To the top
		for r in range(row + 1, 8, +1):
			if self.is_empty_tile(r, col):
				moves.append(Move(piece, r, col, row, col))
			elif self.is_capturable_tile(r, col):
				moves.append(Move(piece, r, col, row, col, self._capture))
				break
			else:
				break
		# To the bottom
		for r in range(row - 1, -1, -1):
			if self.is_empty_tile(r, col):
				moves.append(Move(piece, r, col, row, col))
			elif self.is_capturable_tile(r, col):
				moves.append(Move(piece, r, col, row, col, self._capture))
				break
			else:
				break
		return moves

	def get_moves_for_bishop(self, row, col, piece = BISHOP):
		moves = []
		# To Top-Right
		r, c = row + 1, col + 1
		while r < 8 and c < 8:
			if self.is_empty_tile(r, c):
				moves.append(Move(piece, r, c, row, col))
			elif self.is_capturable_tile(r, c):
				moves.append(Move(piece, r, c, row, col, self._capture))
				break
			else:
				break
			r, c = r + 1, c + 1
		# To Top-Left
		r, c = row + 1, col - 1
		while r < 8 and c >= 0:
			if self.is_empty_tile(r, c):
				moves.append(Move(piece, r, c, row, col))
			elif self.is_capturable_tile(r, c):
				moves.append(Move(piece, r, c, row, col, self._capture))
				break
			else:
				break
			r, c = r + 1, c - 1
		# To Bottom-Left
		r, c = row - 1, col - 1
		while r >= 0 and c >= 0:
			if self.is_empty_tile(r, c):
				moves.append(Move(piece, r, c, row, col))
			elif self.is_capturable_tile(r, c):
				moves.append(Move(piece, r, c, row, col, self._capture))
				break
			else:
				break
			r, c = r - 1, c - 1
		# To Bottom-Right
		r, c = row - 1, col + 1
		while r >= 0 and c < 8:
			if self.is_empty_tile(r, c):
				moves.append(Move(piece, r, c, row, col))
			elif self.is_capturable_tile(r, c):
				moves.append(Move(piece, r, c, row, col, self._capture))
				break
			else:
				break
			r, c = r - 1, c + 1
		return moves

	def get_moves_for_knight(self, row, col):
		moves = []
		delta = (
			(-2, -1),
			(-2, +1),
			(-1, -2),
			(-1, +2),
			(+1, -2),
			(+1, +2),
			(+2, -1),
			(+2, +1)
		)
		for d in delta:
			# Move
			if self.is_empty_tile(row + d[0], col + d[1]):
				moves.append(Move(KNIGHT, row + d[0], col + d[1], row, col))
			elif self.is_capturable_tile(row + d[0], col + d[1]):
				moves.append(Move(KNIGHT, row + d[0], col + d[1], row, col, self._capture))
		return moves

	def get_moves_for_pawn(self, row, col):
		if self.color_to_play == WHITE:
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
		if self.is_empty_tile(row + sens, col):
			moves.append(Move(PAWN, row + sens, col, row, col))
			# Move two tiles
			if (init_row and self.is_empty_tile(row + 2*sens, col)):
				moves.append(Move(PAWN, row + 2*sens, col, row, col))
		# Capture on left
		if self.is_capturable_tile(row + sens, col - 1):
			moves.append(Move(PAWN, row + sens, col - 1, row, col, self._capture))
		elif ep_row and col > 0 and self.two_push_col == col - 1:
			# Capture en passant
			moves.append(Move(PAWN, row + sens, col - 1, row, col, PAWN, en_passant = True))
		# Capture on right
		if self.is_capturable_tile(row + sens, col + 1):
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
		try:
			return self.tiles[row][col] == None
		except IndexError:
			return False

	def is_capturable_tile(self, row, col):
		if row < 0: return False
		if col < 0: return False
		try:
			piece = self.tiles[row][col]
			if piece == None: return False
			if piece.color == self.color_to_play: return False
			if piece.piece != KING:
				# Store the captured piece to store in move
				self._capture = piece.piece
				return True
			# Check situation
			self._check = True
			return False
		except IndexError:
			return False

	def get_material_value(self):
		material = [0, 0]
		for row in range(8):
			for col in range(8):
				if self.tiles[row][col]:
					material[self.tiles[row][col].color] += self.tiles[row][col].get_material_value()
		return material[self.color_to_play] - material[1 - self.color_to_play]

	def eval(self, coef_t = 1, coef_m = 1):
		"""
		coef_t = Coef for tactical score (mobility)
		coef_m = Coef for material score (material value)
		"""
		mobility = len(self.get_legal_moves())
		if mobility == 0:
			# Mate situation
			return -MATE
		# Swap temporarly color to play to get adversary mobility
		temp, self.color_to_play = self.color_to_play, (1 - self.color_to_play)
		mobility -= len(self.get_legal_moves())
		# Restore color to play
		self.color_to_play = temp
		return (mobility * coef_t) + (self.get_material_value() * coef_m)
		
	def get_best_move(self):
		return self.get_best_move_negamax(3)
		
	def get_best_move_negamax(self, depth):
		score, move = self.negamax(depth, -INFINITY, +INFINITY, 1)
		return move

	def negamax(self, depth, alpha, beta, color):
		"""
		See Negamax with alpha beta pruning
		on https://en.wikipedia.org/wiki/Negamax
		"""
		if depth == 0:
			return self.eval() * color, None
		moves = self.get_legal_moves()
		if len(moves) == 0:
			return self.eval() * color, None
		best_score, best_move = -INFINITY, None
		for m in moves:
			new_pos = self + m
			score, move = new_pos.negamax(depth - 1, -beta, -alpha, -color)
			score *= -1
			if score > best_score:
				best_score = score
				best_move = m
			alpha = max(alpha, score)
			if alpha >= beta:
				break
		return best_score, best_move


