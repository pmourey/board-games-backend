from random import choice

import chess
import chess.engine

import pygame

SQUARE_SIZE = 80  # Made smaller for better display
BOARD_SIZE = 8
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE


def draw_board(screen):
	"""Draw the chess board squares"""
	for row in range(BOARD_SIZE):
		for col in range(BOARD_SIZE):
			color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
			pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board, images):
	"""Draw the chess pieces on the board"""
	for square in chess.SQUARES:
		piece = board.piece_at(square)
		if piece:
			# Convert chess.Square to row, col
			row = 7 - chess.square_rank(square)  # Flip row because chess board is displayed bottom-up
			col = chess.square_file(square)

			piece_symbol = piece.symbol()
			if piece_symbol in images:
				screen.blit(images[piece_symbol], (col * SQUARE_SIZE, row * SQUARE_SIZE))


def get_square_from_mouse(pos):
	"""Convert mouse position to chess square"""
	x, y = pos
	col = x // SQUARE_SIZE
	row = y // SQUARE_SIZE
	row = 7 - row  # Flip row because chess board is displayed bottom-up
	return chess.square(col, row)


piece_square_table = {chess.PAWN: [0, 5, 5, 0, 5, 10, 50, 0, 0, 10, -5, 0, 5, 10, 50, 0, 0, 10, 10, 20, 30, 30, 50, 0, 5, 10, 20, 25, 35, 40, 50, 5, 5, 10, 20, 25, 35, 40, 50, 5, 0, 10, 10, 20, 30, 30, 50, 0, 0, 10, -5, 0, 5, 10, 50, 0, 0, 5, 5, 0, 5, 10, 50, 0], chess.KNIGHT: [-50, -40, -30, -30, -30, -30, -40, -50] * 8, chess.BISHOP: [-20, -10, -10, -10, -10, -10, -10, -20] * 8, chess.ROOK: [0, 0, 5, 10, 10, 5, 0, 0] * 8, chess.QUEEN: [-20, -10, -5, -5, -5, -5, -10, -20] * 8, chess.KING: [-30, -40, -40, -50, -50, -40, -40, -30] * 8}


def minimax(board, depth, alpha, beta, maximizing_player):
	if depth == 0 or board.is_game_over():
		return evaluate_board(board)

	legal_moves = list(board.legal_moves)
	if maximizing_player:
		max_eval = float('-inf')
		for move in legal_moves:
			board.push(move)
			eval = minimax(board, depth - 1, alpha, beta, False)
			board.pop()
			max_eval = max(max_eval, eval)
			alpha = max(alpha, eval)
			if beta <= alpha:
				break
		return max_eval
	else:
		min_eval = float('inf')
		for move in legal_moves:
			board.push(move)
			eval = minimax(board, depth - 1, alpha, beta, True)
			board.pop()
			min_eval = min(min_eval, eval)
			beta = min(beta, eval)
			if beta <= alpha:
				break
		return min_eval


def evaluate_board(board):
	piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000}
	evaluation = 0
	for piece_type in piece_values:
		evaluation += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
		evaluation -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

		for square in board.pieces(piece_type, chess.WHITE):
			evaluation += piece_square_table.get(piece_type, [0] * 64)[square]
		for square in board.pieces(piece_type, chess.BLACK):
			evaluation -= piece_square_table.get(piece_type, [0] * 64)[square]

	return evaluation


def find_best_move_old(board, depth=4):
	best_moves = []
	best_value = float('-inf')
	alpha = float('-inf')
	beta = float('inf')

	for move in board.legal_moves:
		board.push(move)
		board_value = minimax(board, depth - 1, alpha, beta, False)
		board.pop()

		if board_value > best_value:
			best_value = board_value
			best_moves = [move]
		elif board_value == best_value:
			best_moves.append(move)
		alpha = max(alpha, best_value)

	return choice(best_moves) if best_moves else None


def find_best_move(board, engine_path="stockfish"):
	with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
		result = engine.play(board, chess.engine.Limit(time=0.1))
		return result.move


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


def main():
	pygame.init()
	screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
	pygame.display.set_caption("Chess Game")
	clock = pygame.time.Clock()

	board = chess.Board()
	images = load_piece_images()
	engine_path = "./stockfish"  # Update this with the correct path to Stockfish if needed

	selected_square = None

	running = True
	while running and not board.is_game_over():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess.WHITE:
				# Player's turn (White)
				clicked_square = get_square_from_mouse(event.pos)

				if selected_square is None:
					# First click - select piece
					piece = board.piece_at(clicked_square)
					if piece and piece.color == chess.WHITE:
						selected_square = clicked_square
				else:
					# Second click - try to make move
					move = chess.Move(selected_square, clicked_square)
					if move in board.legal_moves:
						board.push(move)

						# AI's turn (Black)
						if not board.is_game_over():
							ai_move = find_best_move(board, engine_path)  # Black also uses Stockfish
							if ai_move:
								board.push(ai_move)

					selected_square = None  # Reset selection

		# Draw current game state
		draw_board(screen)
		draw_pieces(screen, board, images)

		# Highlight selected square
		if selected_square is not None:
			row = 7 - chess.square_rank(selected_square)
			col = chess.square_file(selected_square)
			pygame.draw.rect(screen, (255, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

		pygame.display.flip()
		clock.tick(60)

	# Game over
	if board.is_game_over():
		print("Game Over!")
		if board.is_checkmate():
			winner = "Black" if board.turn == chess.WHITE else "White"
			print(f"{winner} wins by checkmate!")
		elif board.is_stalemate():
			print("Draw by stalemate!")

		# Keep window open for a few seconds
		pygame.time.wait(3000)

	pygame.quit()


if __name__ == "__main__":
	main()
