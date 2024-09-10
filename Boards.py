from typing import List, Optional

from flask import jsonify, Response

from Player import Player


class CheckerBoard:
    def __init__(self, rows: int, cols: int, squares: List[str]):
        self.board = [[' '] * cols for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                self.board[i][j] = squares[i * cols + j]
        self.width = cols
        self.height = rows

    def __repr__(self):
        return f'CheckerBoard(board={self.board})'

    def handle_move(self, selected: int, position: int, player: Player, app):
        if not selected:
            return
        s_row, s_col = int(selected // self.width), int(selected % self.height)
        e_row, e_col = int(position // self.width), int(position % self.height)
        piece = self.board[e_row][e_col]
        app.logger.debug(f'(e_row, e_col) = {(e_row, e_col)}')
        app.logger.debug(f'(s_row, s_col) = {(s_row, s_col)}')
        app.logger.debug(f"Piece = {piece}")
        app.logger.debug(f"type player = {type(player)}")
        # Check if the square is empty
        if piece == ' ' and self.is_valid_move(selected, position):
            color = player.color  # Get the color of the player making the move
            app.logger.debug(f"Player = {player} - color = {color}")
            # Update the board state with the new position of the piece
            self.board[e_row][e_col] = color  # 'M' represents a moved piece
            self.board[s_row][s_col] = ' '  # Clear the original square

            # # Check for possible captures
            # possible_captures = self.find_possible_captures(row, col)
            # if possible_captures:
            #     # Perform the capture(s)
            #     for captured_row, captured_col in possible_captures:
            #         self.board[captured_row][captured_col] = ' '

    @property
    def check_winner(self) -> Optional[str]:
        black_pieces = [p for row in self.board for p in row if p == 'B']
        white_pieces = [p for row in self.board for p in row if p == 'W']
        return 'W' if not black_pieces else 'B' if not white_pieces else None

    @property
    def status(self) -> str:
        return 'New Game'

    def find_possible_captures(self, position, player):
        row, col = int(position // len(self.board[0])), int(position % len(self.board))
        possible_captures = []
        # Implement logic to find possible captures
        # This could involve iterating over neighboring squares and checking if a capture is possible
        # For simplicity, let's assume a piece can only capture diagonally forward
        forward_row = row - 1 if self.board[row][col] == 'W' else row + 1
        left_col = col - 1
        right_col = col + 1
        if 0 <= forward_row < 8:
            if 0 <= left_col < 8 and self.board[forward_row][left_col] != ' ' and self.board[forward_row][left_col] != 'M':
                # Capture is possible to the left
                possible_captures.append((forward_row, left_col))
            if 0 <= right_col < 8 and self.board[forward_row][right_col] != ' ' and self.board[forward_row][right_col] != 'M':
                # Capture is possible to the right
                possible_captures.append((forward_row, right_col))
        return possible_captures

    def is_valid_move(self, selected, position):
        # Get row and column of the selected and target positions
        s_row, s_col = int(selected // self.width), int(selected % self.height)
        e_row, e_col = int(position // self.width), int(position % self.height)

        # Get the piece at the selected position
        piece = self.board[s_row][s_col]

        # Check if the selected position is empty or out of bounds
        if piece == ' ' or s_row < 0 or s_row >= self.height or s_col < 0 or s_col >= self.width:
            return False

        # Check if the target position is empty or out of bounds
        if self.board[e_row][e_col] != ' ' or e_row < 0 or e_row >= self.height or e_col < 0 or e_col >= self.width:
            return False

        # Check if the move is diagonal and within the allowed range
        if abs(s_row - e_row) == abs(s_col - e_col) and abs(s_row - e_row) == 1:
            # Check if white piece is moving down or black piece is moving up
            if (piece == 'W' and e_row > s_row) or (piece == 'B' and e_row < s_row):
                return True
        return False

    def get_possible_moves(self, selected, position):
        s_row, s_col = int(selected // len(self.board[0])), int(selected % len(self.board))
        e_row, e_col = int(position // len(self.board[0])), int(position % len(self.board))
        piece = self.board[s_row][s_col]
        possible_moves = []

        if piece == 'W':
            # White piece can move diagonally upwards
            if s_row > 0:
                # Left diagonal
                if s_col > 0 and self.board[s_row - 1][s_col - 1] == ' ':
                    possible_moves.append((s_row - 1, s_col - 1))
                # Right diagonal
                if s_col < 7 and self.board[s_row - 1][s_col + 1] == ' ':
                    possible_moves.append((s_row - 1, s_col + 1))
        elif piece == 'B':
            # Black piece can move diagonally downwards
            if s_row < 7:
                # Left diagonal
                if s_col > 0 and self.board[s_row + 1][s_col - 1] == ' ':
                    possible_moves.append((s_row + 1, s_col - 1))
                # Right diagonal
                if s_col < 7 and self.board[s_row + 1][s_col + 1] == ' ':
                    possible_moves.append((s_row + 1, s_col + 1))

        return possible_moves

    def print_board(self):
        for row in self.board:
            print(' '.join(row))

class TicTacToeBoard:
    pass


class Connect4Board:
    pass

if __name__ == "__main__":
    # checkerboard = CheckerBoard()
    # checkerboard.print_board()
    # checkerboard.handle_move(2, 3)
    # print("\nAfter move:\n")
    # checkerboard.print_board()
    # Example usage
    checker_board = CheckerBoard()
    possible_moves = checker_board.get_possible_moves(2, 2)
    print("Possible moves for piece at (2, 2):", possible_moves)


