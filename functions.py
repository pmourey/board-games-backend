from typing import Optional


def make_move(app, position: int, player: str):
    squares: dict = app.state["squares"]
    app.logger.debug(f'game_board = {squares}')
    if squares[position] is None:
        squares[position] = player
        app.state["xIsNext"] = not app.state["xIsNext"]
        app.logger.debug("move OK")
        return True
    return False

def check_winner(app) -> Optional[str]:
    squares: list = app.state["squares"]
    # Définition des lignes, colonnes et diagonales gagnantes
    winning_positions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # lignes
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # colonnes
        [0, 4, 8], [2, 4, 6]               # diagonales
    ]
    # Vérification des positions gagnantes
    for positions in winning_positions:
        symbols = [squares[pos] for pos in positions]
        if symbols[0] != ' ' and symbols[0] == symbols[1] == symbols[2]:
            return symbols[0]  # Le symbole du gagnant
    if all(square is not None for square in squares):
        return "Draw"  # Match nul (aucun gagnant)
    return None  # Pas de gagnant
