import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
SQUARE_SIZE = 120
BOARD_SIZE = 8
WIDTH, HEIGHT = SQUARE_SIZE * BOARD_SIZE, SQUARE_SIZE * BOARD_SIZE
FPS = 60

# Colors for pieces
WHITE_PIECE = (255, 255, 255)
BLACK_PIECE = (0, 0, 0)

# Piece setup (initial positions)
INITIAL_BOARD = [["r", "n", "b", "q", "k", "b", "n", "r"], ["p", "p", "p", "p", "p", "p", "p", "p"], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["P", "P", "P", "P", "P", "P", "P", "P"], ["R", "N", "B", "Q", "K", "B", "N", "R"]]

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess - Player vs Computer")

# Fonts
font = pygame.font.SysFont("Arial", 24)


# Define the piece images
def load_piece_images():
	white_pieces = ["P", "R", "N", "B", "Q", "K"]
	black_pieces = ["p", "r", "n", "b", "q", "k"]
	pieces = {'b': black_pieces, 'w': white_pieces}
	images = {}
	for color in ["w", "b"]:
		for piece in pieces[color]:
			img = pygame.image.load(f"images/chess-{color}{piece}.png")
			img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
			images[piece] = img
	return images


# Draw the board
def draw_board(board, images):
	screen.fill(WHITE)
	for row in range(BOARD_SIZE):
		for col in range(BOARD_SIZE):
			color = WHITE if (row + col) % 2 == 0 else GRAY
			pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

			piece = board[row][col]
			if piece:
				screen.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))


# Convert mouse position to board coordinates
def mouse_to_board(pos):
	x, y = pos
	return x // SQUARE_SIZE, y // SQUARE_SIZE



# Check if move is valid (now for all pieces)
def is_valid_move(board, start, end, player_color):
	sx, sy = start
	ex, ey = end
	piece = board[sy][sx]
	target_piece = board[ey][ex]

	# Ensure that the end coordinates are within bounds
	if ex < 0 or ex >= BOARD_SIZE or ey < 0 or ey >= BOARD_SIZE:
		return False

	# Check if the piece belongs to the player
	if (player_color == "w" and piece.islower()) or (player_color == "b" and piece.isupper()):
		return False

	# **NEW CHECK: Prevent capturing own piece**
	if target_piece and ((player_color == "w" and target_piece.isupper()) or (player_color == "b" and target_piece.islower())):
		return False  # Cannot capture own piece

	# Define the move patterns for different pieces
	if piece.lower() == "p":  # Pawn
		if player_color == "w":
			if sy == 6 and ey == 4 and sx == ex and not board[ey][ex] and not board[ey + 1][ex]:
				return True  # Pawn's first move (2 squares forward)
			elif ey == sy - 1 and sx == ex and not board[ey][ex]:
				return True  # Normal pawn move (1 square forward)
			elif ey == sy - 1 and abs(ex - sx) == 1 and board[ey][ex] and board[ey][ex].islower():
				return True  # Pawn captures diagonally
		elif player_color == "b":
			if sy == 1 and ey == 3 and sx == ex and not board[ey][ex] and not board[ey - 1][ex]:
				return True  # Pawn's first move (2 squares forward)
			elif ey == sy + 1 and sx == ex and not board[ey][ex]:
				return True  # Normal pawn move (1 square forward)
			elif ey == sy + 1 and abs(ex - sx) == 1 and board[ey][ex] and board[ey][ex].isupper():
				return True  # Pawn captures diagonally

	elif piece.lower() == "r":  # Rook
		if sx == ex:  # Vertical move
			step = 1 if sy < ey else -1
			for i in range(sy + step, ey, step):
				if board[i][sx]:
					return False  # Blocked
			return True
		elif sy == ey:  # Horizontal move
			step = 1 if sx < ex else -1
			for i in range(sx + step, ex, step):
				if board[sy][i]:
					return False  # Blocked
			return True

	elif piece.lower() == "n":  # Knight
		if (abs(sx - ex) == 1 and abs(sy - ey) == 2) or (abs(sx - ex) == 2 and abs(sy - ey) == 1):
			return True  # L-shaped move

	elif piece.lower() == "b":  # Bishop
		if abs(sx - ex) == abs(sy - ey):  # Diagonal move
			step_x = 1 if ex > sx else -1
			step_y = 1 if ey > sy else -1
			x, y = sx + step_x, sy + step_y
			while x != ex and y != ey:
				if board[y][x]:
					return False  # Blocked
				x += step_x
				y += step_y
			return True

	elif piece.lower() == "q":  # Queen
		# Queen moves like a rook and a bishop
		if sx == ex:  # Vertical move
			step = 1 if sy < ey else -1
			for i in range(sy + step, ey, step):
				if board[i][sx]:
					return False  # Blocked
			return True
		elif sy == ey:  # Horizontal move
			step = 1 if sx < ex else -1
			for i in range(sx + step, ex, step):
				if board[sy][i]:
					return False  # Blocked
			return True
		elif abs(sx - ex) == abs(sy - ey):  # Diagonal move
			step_x = 1 if ex > sx else -1
			step_y = 1 if ey > sy else -1
			x, y = sx + step_x, sy + step_y
			while x != ex and y != ey:
				if board[y][x]:
					return False  # Blocked
				x += step_x
				y += step_y
			return True

	elif piece.lower() == "k":  # King
		if abs(sx - ex) <= 1 and abs(sy - ey) <= 1:
			return True  # King moves one square in any direction


	return False


def is_square_under_attack(board, square, attacking_color):
	"""Check if a square is under attack by any piece of the given color"""
	ex, ey = square
	for y in range(len(board)):
		for x in range(len(board[0])):
			piece = board[y][x]
			if piece and (piece.isupper() == attacking_color):
				if is_valid_move(board, (x, y), (ex, ey), "w" if attacking_color else "b"):
					return True
	return False


def find_king(board, is_white):
	"""Find the position of the king"""
	king = 'K' if is_white else 'k'
	for y in range(len(board)):
		for x in range(len(board[0])):
			if board[y][x] == king:
				return (x, y)
	return None


def is_in_check(board, is_white):
	"""Determine if the specified king is in check"""
	king_pos = find_king(board, is_white)
	if not king_pos:
		return False
	return is_square_under_attack(board, king_pos, not is_white)


def get_valid_moves(board, start, is_white):
	"""Get all valid moves for a piece that don't leave the king in check"""
	valid_moves = []
	sx, sy = start
	piece = board[sy][sx]

	# Check if it's the correct color piece
	if (piece.isupper() != is_white) or not piece:
		return valid_moves

	# Special handling for king moves
	is_king = piece.lower() == 'k'
	player_color = "w" if is_white else "b"

	# Try all possible squares
	for ey in range(len(board)):
		for ex in range(len(board[0])):
			if is_valid_move(board, start, (ex, ey), player_color):
				if is_king:
					# For king moves, check if target square is under attack
					temp_piece = board[ey][ex]
					board[ey][ex] = piece
					board[sy][sx] = ""

					# Don't allow move if square is under attack
					if not is_square_under_attack(board, (ex, ey), not is_white):
						valid_moves.append((ex, ey))

					# Undo temporary move
					board[sy][sx] = piece
					board[ey][ex] = temp_piece
				else:
					# For other pieces, check if move prevents/resolves check
					temp_piece = board[ey][ex]
					board[ey][ex] = piece
					board[sy][sx] = ""

					if not is_in_check(board, is_white):
						valid_moves.append((ex, ey))

					# Undo temporary move
					board[sy][sx] = piece
					board[ey][ex] = temp_piece

	return valid_moves


def is_checkmate(board, is_white):
	"""Determine if the position is checkmate"""
	# First check if king is in check
	if not is_in_check(board, is_white):
		return False

	# Check if any piece has valid moves
	for y in range(len(board)):
		for x in range(len(board[0])):
			piece = board[y][x]
			if piece and (piece.isupper() == is_white):
				if get_valid_moves(board, (x, y), is_white):
					return False
	return True

def make_move(board, start, end):
	"""Make a move and check for game over"""
	sx, sy = start
	ex, ey = end
	piece = board[sy][sx]
	is_white = piece.isupper()

	# Validate the move
	valid_moves = get_valid_moves(board, start, is_white)
	if (ex, ey) not in valid_moves:
		return "Invalid move"

	# Make the move
	board[ey][ex] = piece
	board[sy][sx] = ""

	# Pawn Promotion Check
	if piece.lower() == "p" and (ey == 0 or ey == 7):  # White promotes at row 0, Black at row 7
		board[ey][ex] = "Q" if is_white else "q"  # Auto-promote to Queen (modify for choice)

	# Check opponent's situation
	opponent_is_white = not is_white
	if is_checkmate(board, opponent_is_white):
		return "Checkmate! Game Over"
	elif is_in_check(board, opponent_is_white):
		return "Check!"

	return None


def validate_move(board, start, end, is_white):
	"""Validate a move before making it"""
	sx, sy = start
	piece = board[sy][sx]

	# Basic validation
	if not piece or (piece.isupper() != is_white):
		return False

	# Get valid moves
	valid_moves = get_valid_moves(board, start, is_white)
	return end in valid_moves


# Example usage
def play_turn(board, start, end, is_white):
	"""Handle a complete turn with validation"""
	if not validate_move(board, start, end, is_white):
		return "Invalid move"

	status = make_move(board, start, end)
	return status


def ai_move(board):
	# First check if AI's king is in check
	is_ai_in_check = is_in_check(board, False)  # False for black/AI pieces

	# Find AI's king position if in check
	if is_ai_in_check:
		king_pos = find_king(board, False)
		if king_pos:
			# Get valid moves for the king
			king_valid_moves = []
			kx, ky = king_pos
			for dy in range(-1, 2):
				for dx in range(-1, 2):
					ex, ey = kx + dx, ky + dy
					if 0 <= ex < BOARD_SIZE and 0 <= ey < BOARD_SIZE:
						if is_valid_move(board, (kx, ky), (ex, ey), "b"):
							# Test if this move gets us out of check
							temp_piece = board[ey][ex]
							board[ey][ex] = board[ky][kx]
							board[ky][kx] = ""

							if not is_in_check(board, False):
								king_valid_moves.append(((kx, ky), (ex, ey)))

							# Undo move
							board[ky][kx] = board[ey][ex]
							board[ey][ex] = temp_piece

			# If there are valid king moves, choose one randomly
			if king_valid_moves:
				return random.choice(king_valid_moves)

			# If no valid king moves, look for pieces that can block check or capture
			blocking_moves = []
			for y in range(BOARD_SIZE):
				for x in range(BOARD_SIZE):
					piece = board[y][x]
					if piece and piece.islower():  # AI's pieces
						for dy in range(-1, 2):
							for dx in range(-1, 2):
								ex, ey = x + dx, y + dy
								if 0 <= ex < BOARD_SIZE and 0 <= ey < BOARD_SIZE:
									if is_valid_move(board, (x, y), (ex, ey), "b"):
										# Test if this move blocks the check
										temp_piece = board[ey][ex]
										board[ey][ex] = board[y][x]
										board[y][x] = ""

										if not is_in_check(board, False):
											blocking_moves.append(((x, y), (ex, ey)))

										# Undo move
										board[y][x] = board[ey][ex]
										board[ey][ex] = temp_piece

			if blocking_moves:
				return random.choice(blocking_moves)

			return None  # No valid moves - checkmate

	# If not in check, proceed with normal move selection
	valid_moves = []
	for y in range(BOARD_SIZE):
		for x in range(BOARD_SIZE):
			piece = board[y][x]
			if piece and piece.islower():  # AI's pieces
				for dy in range(-1, 2):
					for dx in range(-1, 2):
						ex, ey = x + dx, y + dy
						if 0 <= ex < BOARD_SIZE and 0 <= ey < BOARD_SIZE:
							if is_valid_move(board, (x, y), (ex, ey), "b"):
								# Verify move doesn't put own king in check
								temp_piece = board[ey][ex]
								board[ey][ex] = board[y][x]
								board[y][x] = ""

								if not is_in_check(board, False):
									valid_moves.append(((x, y), (ex, ey)))

								# Undo move
								board[y][x] = board[ey][ex]
								board[ey][ex] = temp_piece

	if valid_moves:
		return random.choice(valid_moves)
	return None


# Main game loop
def game_loop():
	board = [row[:] for row in INITIAL_BOARD]
	images = load_piece_images()
	player_turn = True  # True for player, False for AI
	selected_piece = None
	selected_pos = None

	while True:
		screen.fill(WHITE)
		draw_board(board, images)
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == pygame.MOUSEBUTTONDOWN:
				x, y = event.pos
				col, row = mouse_to_board((x, y))

				if selected_piece:
					if is_valid_move(board, selected_pos, (col, row), "w" if player_turn else "b"):
						make_move(board, selected_pos, (col, row))
						player_turn = not player_turn  # Switch turn
					# **Reset selection even if move is invalid**
					selected_piece = None
					selected_pos = None
				else:
					if board[row][col]:  # If there's a piece on clicked square
						piece = board[row][col]
						if (player_turn and piece.isupper()) or (not player_turn and piece.islower()):
							selected_piece = piece
							selected_pos = (col, row)

		if not player_turn:  # AI's turn
			move = ai_move(board)
			if move:
				start, end = move
				make_move(board, start, end)
				player_turn = not player_turn
			else:
				if is_checkmate(board, False):
					print("Player wins by checkmate!")
					input("Press Enter to exit...")
					break

		pygame.display.flip()
		pygame.time.Clock().tick(FPS)


game_loop()
