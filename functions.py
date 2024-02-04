from typing import Optional

""" TIC TAC TOE """


def make_move_ttt(app, position: int, player: str):
    squares: dict = app.state_ttt["squares"]
    app.logger.debug(f'game_board = {squares}')
    if squares[position] is None:
        squares[position] = player
        app.state_ttt["xIsNext"] = not app.state_ttt["xIsNext"]
        app.logger.debug("move OK")
        return True
    return False


# obsolete
def check_winner_ttt_3x3(app) -> Optional[str]:
    squares: list = app.state_ttt["squares"]
    # Définition des lignes, colonnes et diagonales gagnantes
    winning_positions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # lignes
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # colonnes
        [0, 4, 8], [2, 4, 6]  # diagonales
    ]
    # Vérification des positions gagnantes
    for positions in winning_positions:
        symbols = [squares[pos] for pos in positions]
        if symbols[0] != ' ' and symbols[0] == symbols[1] == symbols[2]:
            return symbols[0]  # Le symbole du gagnant
    if all(square is not None for square in squares):
        return "Draw"  # Match nul (aucun gagnant)
    return None  # Pas de gagnant


def check_winner_ttt(app) -> Optional[str]:
    squares: list = app.state_ttt["squares"]
    size = int(len(squares) ** 0.5)  # Calculate the size of the grid

    # Define winning positions for rows, columns, and diagonals
    winning_positions = []
    for i in range(size):
        winning_positions.append(list(range(i * size, (i + 1) * size)))  # Rows
        winning_positions.append(list(range(i, size ** 2, size)))  # Columns
    winning_positions.append(list(range(0, size ** 2, size + 1)))  # Diagonal \
    winning_positions.append(list(range(size - 1, size ** 2 - size + 1, size - 1)))  # Diagonal /

    # Check winning positions
    for positions in winning_positions:
        symbols = [squares[pos] for pos in positions]
        if symbols[0] != ' ' and all(symbol == symbols[0] for symbol in symbols):
            return symbols[0]  # Winning symbol
    if all(square is not None for square in squares):
        return "Draw"  # Draw (no winner)
    return None  # No winner


""" CONNECT 4 """


def is_valid_column(board, column):
    return 0 <= column < len(board[0])  # and all(row[column] is not None for row in board)


def drop_piece(app, column, player):
    board = app.state_c4["squares"]
    # app.logger.debug(board)
    rows, cols = 6, 7
    board = [board[i:i + cols] for i in range(0, len(board), cols)]
    app.logger.debug(board)
    for row in range(len(board) - 1, -1, -1):
        if board[row][column] is None:
            board[row][column] = player
            return row
    return None


def check_winner(board):
    # Check horizontal
    for row in range(len(board)):
        for col in range(len(board[0]) - 3):
            if board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3] and board[row][col] is not None:
                return board[row][col]

    # Check vertical
    for col in range(len(board[0])):
        for row in range(len(board) - 3):
            if board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col] and board[row][col] is not None:
                return board[row][col]

    # Check diagonal (top-left to bottom-right)
    for row in range(len(board) - 3):
        for col in range(len(board[0]) - 3):
            if board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3] and board[row][col] is not None:
                return board[row][col]

    # Check diagonal (top-right to bottom-left)
    for row in range(3, len(board)):
        for col in range(len(board[0]) - 3):
            if board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3] and board[row][col] is not None:
                return board[row][col]

    # If no winner found, return None
    return None
