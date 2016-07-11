from .const import *
from .move import Move
from .position import Position

import re
import winsound

HELP = """
h: Show this help
l: Show legal moves
m: Show material score
e: Show evaluation
g: Show game moves
c: Let computer choose for me
u: Undo last move
q: Quit

NUMBER: Choose move by number in legal moves list
MOVE: Play the move if valid
"""
class Game:

	def __init__(self, white = HUMAN, black = COMPUTER):
		# Current position is regular start position
		self.position = Position()
		self.position.start()
		# List of moves is empty
		self.moves = []
		# Opponents, by default black opponent is computer and white is human
		self.opponents = [black, white]
		
	def __str__(self):
		s = ""
		for i, m in enumerate(self.moves):
			# Turn number
			if i % 2 == 0:
				if i > 0: s += "\n" # New Line
				s += str((i // 2) + 1)
				s += ". "
			# Move
			s += str(m)
			s += "\t"
		return s

	def play(self):
		while 1:
			# Show current position
			print(self.position)
			# Get move
			if self.opponents[self.position.color_to_play] == HUMAN:
				if len(self.position.get_legal_moves(self.position.color_to_play)) == 0:
					print("{} wins !!".format(COLOR_NAMES[1 - self.position.color_to_play]))
					quit()
				move = self.get_human_move()
			else:
				move = self.get_computer_move()
				winsound.Beep(500, 2000)
				if not move:
					print("{} wins !!".format(COLOR_NAMES[1 - self.position.color_to_play]))
					quit()
			# Print move
			print("{} move: {}".format(COLOR_NAMES[self.position.color_to_play], move))
			# Play move
			self.position.play(move)
			# Store move
			self.moves.append(move)

	def get_human_move(self):
		while 1:
			s = input("{} move: ".format(COLOR_NAMES[self.position.color_to_play]))
			if s == "h":
				print(HELP)
			elif s == "l":
				# Show legal moves
				legal_moves = self.position.get_legal_moves(self.position.color_to_play)
				for i, m in enumerate(legal_moves):
					print(str(i + 1) + ": " + str(m))
			elif s == "m":
				# Show material value
				print("Material value: " + str(self.position.get_material_value()))
			elif s == "e":
				# Show evaluation
				print("Score {}: {}".format(COLOR_NAMES[self.position.color_to_play], self.position.eval()))
			elif s == "g":
				#  Show game moves
				print(self)
			elif s == "c":
				# Let computer choose for me
				print("Computer's advice: {}".format(self.position.get_best_move()))
			elif s == "u":
				# Undo the last move
				self.position.unplay(self.moves.pop(-1))
				# Undo the computer move if it played
				if self.opponents[self.position.color_to_play] == COMPUTER:
					self.position.unplay(self.moves.pop(-1))
				print(self.position)
			elif s == "q":
				# Quit
				quit()
			elif re.match(r"^[1-9][0-9]*$", s):
				# Choose move by number in possible moves list
				legal_moves = self.position.get_legal_moves(self.position.color_to_play)
				if int(s) in range(1, len(legal_moves) + 1):
					return legal_moves[int(s) - 1]
			else:
				move = Move.parse(s)
				if move:
					if self.position.resolve_move(move):
						if self.position.check_move(move):
							return move
						else:
							print("Move {} is not legal".format(move))

	def get_computer_move(self):
		return self.position.get_best_move()
