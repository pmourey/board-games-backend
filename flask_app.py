import copy
import os
import ssl
from random import randint, choice
from typing import List, Optional

from flask import Flask, request, jsonify, json

from GameState import GameState
from Player import Player
from functions import make_move_ttt, check_winner, is_valid_column, drop_piece, check_winner_ttt, check_winner_ttt_3x3
from flask_cors import CORS, cross_origin
from config import Config
from _socket import gethostbyname
from Boards import CheckerBoard

app = Flask(__name__, static_folder='static', static_url_path='/static')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config.from_object('config.Config')

# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = app.config.SECRET_KEY

BOARD_SIZE_TTT = 9
BOARD_SIZE_C4 = 42
BOARD_WIDTH_C4 = 7
BOARD_SIZE_CHECKERS = 64

app.init_state_ttt = {
    "squares": [None] * BOARD_SIZE_TTT,
    "xIsNext": True,
    "gameOver": False,
    "status": "New game",
    "numPlayers": 1,
    "winner": None
}

app.init_state_c4 = {
    "squares": [None] * BOARD_SIZE_C4,
    "xIsNext": True,
    "gameOver": False,
    "status": "New game",
    "numPlayers": 1,
    "winner": None
}

app.init_state_checkers = {
    "squares": [None] * BOARD_SIZE_CHECKERS,
    "xIsNext": True,
    "gameOver": False,
    "status": "New game",
    "numPlayers": 1,
    "winner": None
}

app.state_ttt = copy.deepcopy(app.init_state_ttt)
app.state_c4 = copy.deepcopy(app.init_state_c4)
app.state_checkers = GameState(board=None, players=[], last_player=None)


@app.route('/get_ip')
def get_ip():
    # Obtenir l'adresse IP du client
    client_ip = request.remote_addr
    # Obtenir le nom d'hôte du serveur
    server_hostname = request.host.split(':')[0]
    # Résoudre le nom d'hôte en adresse IP
    server_ip = gethostbyname(server_hostname)
    return f"Adresse IP du client : {client_ip}\nAdresse IP du serveur : {server_ip}"


# @cross_origin()
@app.route('/api/new_game_ttt', methods=['POST'])
def new_game_ttt():
    app.state_ttt = copy.deepcopy(app.init_state_ttt)
    return jsonify(app.state_ttt), 200


@app.route('/api/new_game_c4', methods=['POST'])
def new_game_c4():
    try:
        num_players = request.json.get('players')
        app.state_c4 = copy.deepcopy(app.init_state_c4)
        app.state_c4["numPlayers"] = num_players
        if num_players == 1:
            pass
        return jsonify(app.state_c4), 200

    except ValueError as e:
        return jsonify({'error': request.on_json_loading_failed(e)}), 500



@app.route('/api/move_ttt', methods=['POST'])
def move_ttt():
    app.logger.debug(f'game_board = {app.state_ttt["squares"]}')
    # app.logger.debug(f'request.json = {request.json}')
    try:
        position = request.json.get('move')
        player = request.json.get('player')
        app.logger.debug(f'position = {position} - player = {player}')

        app.state_ttt["winner"] = check_winner_ttt(app)

        if app.state_ttt["winner"] is not None:
            # app.state_c4["status"] = f"Winner: " + app.state_c4["winner"] if app.state_c4["winner"] != 'Draw' else " - Draw!"
            if app.state_ttt["winner"] == 'Draw':
                app.state_ttt["status"] = f"Game Over - It is a Draw!"
            else:
                app.state_ttt["status"] = f"Game Over - Player {app.state_ttt['winner']} wins"
            app.state_ttt["gameOver"] = True
            return jsonify(app.state_ttt), 400

        if position is None or player not in ['X', 'O']:
            app.state_ttt["status"] = "Invalid position"
            return jsonify({'error': 'Invalid request parameters'}), 400

        position = int(position)  # Convertir en entier
        if position < 0 or position >= BOARD_SIZE_TTT:
            app.state_ttt["status"] = "Invalid position"
            return jsonify(app.state_ttt), 400

        if make_move_ttt(app, position, player):
            app.state_ttt["winner"] = check_winner_ttt(app)
            app.state_ttt["gameOver"] = True if app.state_ttt["winner"] else False
            app.state_ttt["status"] = f"Player {player} on {position}" if app.state_ttt["winner"] is None \
                else "Winner: " + app.state_ttt["winner"] if app.state_ttt["winner"] != 'Draw' else "Draw!"
        else:
            app.state_ttt["status"] = "Invalid move"
            return jsonify({'error': 'Invalid request parameters'}), 400

        app.logger.debug(f'status = {app.state_ttt["status"]}')

        if app.state_ttt["numPlayers"] == 1 and not app.state_ttt["gameOver"]:
            # Computer plays
            player = 'O'
            computer_moves = [x for x in range(BOARD_SIZE_TTT) if not app.state_ttt["squares"][x]]
            position = choice(computer_moves)
            app.state_ttt["squares"][position] = 'O'
            app.state_ttt["xIsNext"] = True
            app.state_ttt["winner"] = check_winner_ttt(app)
            app.logger.debug(f'winner = {app.state_ttt["winner"]}')
            app.state_ttt["gameOver"] = True if app.state_ttt["winner"] else False
            app.logger.debug(f'gameOver = {app.state_ttt["gameOver"]}')
            app.state_ttt["status"] += f" - Computer {player} on position {position}" if app.state_ttt["winner"] is None \
                else " - Winner: " + app.state_ttt["winner"] if app.state_ttt["winner"] != 'Draw' else " - Draw!"

        return jsonify(app.state_ttt), 200

    except ValueError as e:
        return jsonify({'error': request.on_json_loading_failed(e)}), 500


@app.route('/api/move_c4', methods=['POST'])
def move_c4():
    rows, cols = 6, 7
    board = app.state_c4["squares"]
    board = [board[i:i + cols] for i in range(0, len(board), cols)]
    # app.logger.debug(f'game_board = {board}')
    # app.logger.debug(f'request = {request}')
    try:
        column = int(request.json.get('column'))  # Extract the column from the request
        player = request.json.get('player').get('type')
        app.logger.debug(f'player = {player} - column = {column}')

        if column is None or player not in ['X', 'O']:
            app.state_c4["status"] = "Invalid move"
            return jsonify({'error': 'Invalid request parameters'}), 400

        if not is_valid_column(board, column):
            app.logger.debug(f'column {column} is not valid')
            app.state_c4["status"] = "Invalid move"
            return jsonify(app.state_c4), 400

        row = drop_piece(app, column, player)
        if row is None:
            app.logger.debug(f'drop row = {row}')
            app.state_c4["status"] = "Column is full"
            return jsonify(app.state_c4), 400

        # Player action
        board[row][column] = player

        winner = check_winner(board)
        # app.logger.debug(f'winner = {winner}')
        app.state_c4["winner"] = winner

        app.state_c4["gameOver"] = True if winner else False
        app.state_c4["status"] = f"Player {player} in column {column} and row {row}" if winner is None \
            else f"Winner: {winner}" if winner != 'Draw' else "Draw!"
        app.state_c4["squares"] = [item for sublist in board for item in sublist]
        app.state_c4["xIsNext"] = not app.state_c4["xIsNext"]

        # app.logger.debug(f'state_c4 = {app.state_c4}')

        if app.state_c4["numPlayers"] == '1' and not app.state_c4["gameOver"]:
            # Computer action
            player = 'O'
            computer_moves = [c for c in range(BOARD_WIDTH_C4) if is_valid_column(board, c)]
            # app.logger.debug(f'Computer moves: {computer_moves}')
            column = choice(computer_moves)
            row = drop_piece(app, column, player)
            board[row][column] = player
            app.logger.debug(f'player = {player} - column = {column}')
            app.state_c4["squares"] = [item for sublist in board for item in sublist]
            app.state_c4["xIsNext"] = True
            winner = check_winner(board)
            # app.logger.debug(f'winner = {winner}')
            app.state_c4["winner"] = winner
            app.state_c4["gameOver"] = True if winner else False
            # app.logger.debug(f'gameOver = {app.state_c4["gameOver"]}')
            app.state_c4["status"] += f" - Computer {player} in column {column} and row {row}" if winner is None \
                else f" - Winner: {winner}" if app.state_c4["winner"] != 'Draw' else " - Draw!"

        # app.logger.debug(f'state_c4 = {app.state_c4}')
        return jsonify(app.state_c4), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new_game_checkers', methods=['POST'])
def new_game_checkers():
    try:
        input_state = request.json.get('state')
        rows = request.json.get('rows')
        cols = request.json.get('cols')
        app.logger.debug(f'input_state = {input_state} type {type(input_state)}- rows = {rows} - cols = {cols}')
        app.state_checkers.board = CheckerBoard(rows=rows, cols=cols, squares=input_state['squares'])
        other_player_type: str = 'Computer'  # if num_players == 1 else 'Human'
        app.state_checkers.players = [Player(id=1, type='Human', color='B'), Player(id=2, type=other_player_type, color='W')]
        app.logger.debug(f'input_state type: {type(input_state)}')
        last_player_id: int = input_state['nextPlayer']['id']

        app.logger.debug(f'last_player_id = {last_player_id}')
        app.state_checkers.last_player = app.state_checkers.players[last_player_id - 1]
        app.logger.debug(f'app.state_checkers = {app.state_checkers}')
        return app.state_checkers.to_json, 200

    except ValueError as e:
        return jsonify({'error': request.on_json_loading_failed(e)}), 500

@app.route('/api/move_checkers', methods=['POST'])
def move_checkers():
    try:
        selected = request.json.get('selected')
        position = request.json.get('move')
        player = json.loads(request.json.get('player'))
        app.logger.debug(f'position = {position} - player = {player}')
        player_id: int = (player['id'] + 1) % len(app.state_checkers.players)
        player = app.state_checkers.players[player_id - 1]

        winner: Optional[str] = app.state_checkers.board.check_winner
        if winner is not None:
            if winner == 'Draw':
                app.state_checkers.status = f"Game Over - It is a Draw!"
            else:
                app.state_checkers.status = f"Game Over - Player {winner} wins"
            return app.state_checkers.to_json, 400

        if app.state_checkers.board.handle_move(selected, position, player, app):
            winner: Optional[str] = app.state_checkers.board.check_winner
            app.state_checkers.game_over = winner is not None
            # last_player_id: int = (player.id + 1) % len(app.state_checkers.players)
            # app.state_checkers.last_player = app.state_checkers.players[last_player_id - 1]
            app.state_checkers.last_move = position
            app.state_checkers.status = f"Player {player} on {position}" if winner is None \
                else "Winner: " + winner if winner != 'Draw' else "Draw!"
        else:
            app.state_checkers.status = "Invalid move"

        app.logger.debug(f'app.state_checkers = {app.state_checkers}')

        if not app.state_checkers.game_over: # len(app.state_checkers.players) == 1 and
            # Computer plays
            rows, cols = app.state_checkers.board.height, app.state_checkers.board.width
            next_player_id: int = (player.id + 1) % len(app.state_checkers.players)
            next_player = app.state_checkers.players[next_player_id - 1]
            computer_moves = [(s, e) for s in range(BOARD_SIZE_CHECKERS) for e in range(BOARD_SIZE_CHECKERS)
                              if app.state_checkers.board.board[s // cols][s % rows] == next_player.color and s != e
                              and app.state_checkers.board.board[e // cols][e % rows] == ' ' and app.state_checkers.board.is_valid_move(s, e)]
            selected, position = choice(computer_moves)
            app.logger.debug(f'computer_moves = {computer_moves} - selected = {selected} - position = {position}')
            app.state_checkers.board.handle_move(selected, position, next_player, app)
            app.state_checkers.last_player = next_player
            app.state_checkers.last_move = position
            winner: Optional[str] = app.state_checkers.board.check_winner
            app.state_checkers.game_over = winner is not None
            app.state_checkers.status += f" - Computer 'W' on position {position}" if winner is None \
                else " - Winner: " + winner if winner != 'Draw' else " - Draw!"

        return app.state_checkers.to_json, 200

    except ValueError as e:
        return jsonify({'error': request.on_json_loading_failed(e)}), 500
