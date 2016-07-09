from .const import *

# Piece class
class Piece:

	def __init__(self, color, piece):
		self.color = color
		self.piece = piece

	def __eq__(self, other):
		return isinstance(other, Piece) and self.piece == other.piece and self.color == other.color

	def __hash__(self):
		return self.piece << 1 | self.color

	def short_str(self):
		s = PIECE_SHORT[self.piece]
		if self.color == BLACK:
			s = s.lower()
		return s

	@staticmethod
	def get_instance(color, piece):
		return (King, Queen, Rook, Bishop, Knight, Pawn)[piece](color)

	def get_material_value(self):
		raise NotImplementedError


# King class
class King(Piece):
	def __init__(self, color):
		super().__init__(color, KING)
	def get_material_value(self):
		return 0


# Queen class
class Queen(Piece):
	def __init__(self, color):
		super().__init__(color, QUEEN)
	def get_material_value(self):
		return 100


# Rook class
class Rook(Piece):
	def __init__(self, color):
		super().__init__(color, ROOK)
	def get_material_value(self):
		return 50


# Bishop class
class Bishop(Piece):
	def __init__(self, color):
		super().__init__(color, BISHOP)
	def get_material_value(self):
		return 30


# Knight class
class Knight(Piece):
	def __init__(self, color):
		super().__init__(color, KNIGHT)
	def get_material_value(self):
		return 30


# Pawn class
class Pawn(Piece):
	def __init__(self, color):
		super().__init__(color, PAWN)
	def get_material_value(self):
		return 10
	def promote(self, piece):
		if piece == QUEEN:
			return Queen(self.color)
		elif piece == KNIGHT:
			return Knight(self.color)
		elif piece == ROOK:
			return Rook(self.color)
		elif piece == BISHOP:
			return Bishop(self.color)
		else:
			raise ValueError

