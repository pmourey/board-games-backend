import copy
import os
import ssl

from flask import Flask, request, jsonify
from functions import make_move, check_winner
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={r"/api/*": {"origins": ["https://192.168.1.10:3000", "https://philippe.mourey.com:1999",
                                             "http://192.168.1.10:3000", "http://philippe.mourey.com:1999"]}})
# CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "http://philippe.mourey.com:1999"}})

PRIVATE_FOLDER = os.path.join('static', 'private')

app.init_state = {
    "squares": [None] * 9,
    "xIsNext": True,
    "gameOver": False,
    "status": "New game",
    "winner": None
}

app.state = copy.deepcopy(app.init_state)


@app.route('/api/new_game', methods=['POST'])
def new_game():
    app.state = copy.deepcopy(app.init_state)
    #app.logger.debug(f'initial_state = {app.state}')
    return jsonify(app.state), 200


@app.route('/api/move', methods=['POST'])
def move():
    app.logger.debug(f'game_board = {app.state["squares"]}')
    # app.logger.debug(f'request.json = {request.json}')
    try:
        position = request.json.get('move')
        player = request.json.get('player')
        app.logger.debug(f'position = {position} - player = {player}')

        if position is None or player not in ['X', 'O']:
            app.state["status"] = "Invalid position"
            return jsonify({'error': 'Invalid request parameters'}), 400

        position = int(position)  # Convertir en entier
        if position < 0 or position >= 9:
            app.state["status"] = "Invalid position"
            return jsonify(app.state), 400

        if make_move(app, position, player):
            app.state["winner"] = check_winner(app)
            app.state["gameOver"] = True if app.state["winner"] else False
            app.state["status"] = f"Player {player} on {position}" if app.state["winner"] is None else "Winner: " + app.state["winner"] if app.state["winner"] != 'Draw' else "Draw!"
        else:
            app.state["status"] = "Invalid move"

        app.logger.debug(app.state["status"])
        return jsonify(app.state), 200

    except ValueError as e:
        return jsonify({'error': request.on_json_loading_failed(e)}), 500


if __name__ == '__main__':
    # Path to SSL certificate and private key files
    # ssl_cert_path = f'{PRIVATE_FOLDER}/cert.pem'
    # ssl_key_path = f'{PRIVATE_FOLDER}/key.pem'
    ssl_cert_path = f'{PRIVATE_FOLDER}/certificate.pem'
    ssl_key_path = f'{PRIVATE_FOLDER}/private_key.pem'

    # Load SSL context with passphrase
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=ssl_cert_path, keyfile=ssl_key_path, password='name of cat')

    # Run the Flask app with HTTPS enabled
    app.run(debug=True, host='0.0.0.0', port=1443, ssl_context=ssl_context)
    # app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=ssl_context)
