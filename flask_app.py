import copy
import os
import ssl

from flask import Flask, request, jsonify
from functions import make_move_ttt, check_winner, is_valid_column, drop_piece, check_winner_ttt
from flask_cors import CORS, cross_origin
from config import Config
from _socket import gethostbyname

app = Flask(__name__, static_folder='static', static_url_path='/static')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config.from_object('config.Config')

# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = app.config.SECRET_KEY

BOARD_SIZE_TTT = 9
BOARD_SIZE_C4 = 42

app.init_state_ttt = {
    "squares": [None] * BOARD_SIZE_TTT,
    "xIsNext": True,
    "gameOver": False,
    "status": "New game",
    "winner": None
}

app.init_state_c4 = {
    "squares": [None] * BOARD_SIZE_C4,
    "xIsNext": True,
    "gameOver": False,
    "status": "New game",
    "winner": None
}

app.state_ttt = copy.deepcopy(app.init_state_ttt)
app.state_c4 = copy.deepcopy(app.init_state_c4)

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
    app.state_c4 = copy.deepcopy(app.init_state_c4)
    return jsonify(app.state_c4), 200


@app.route('/api/move_ttt', methods=['POST'])
def move_ttt():
    app.logger.debug(f'game_board = {app.state_ttt["squares"]}')
    # app.logger.debug(f'request.json = {request.json}')
    try:
        position = request.json.get('move')
        player = request.json.get('player')
        app.logger.debug(f'position = {position} - player = {player}')

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

        app.logger.debug(app.state_ttt["status"])
        return jsonify(app.state_ttt), 200

    except ValueError as e:
        return jsonify({'error': request.on_json_loading_failed(e)}), 500


@app.route('/api/move_c4', methods=['POST'])
def move_c4():
    rows, cols = 6, 7
    board = app.state_c4["squares"]
    board = [board[i:i + cols] for i in range(0, len(board), cols)]
    app.logger.debug(f'game_board = {board}')
    try:
        column = int(request.json.get('column'))  # Extract the column from the request
        player = request.json.get('player')
        app.logger.debug(f'column = {column}')

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

        board[row][column] = player
        app.state_c4["winner"] = check_winner(board)
        app.logger.debug(app.state_c4["winner"])

        app.state_c4["gameOver"] = True if app.state_c4["winner"] else False
        app.state_c4["status"] = f"Player {player} in column {column} and row {row}" if app.state_c4["winner"] is None \
            else "Winner: " + app.state_c4["winner"] if app.state_c4["winner"] != 'Draw' else "Draw!"
        app.state_c4["squares"] = [item for sublist in board for item in sublist]
        app.state_c4["xIsNext"] = not app.state_c4["xIsNext"]

        app.logger.debug(app.state_c4["status"])
        return jsonify(app.state_c4), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 500
