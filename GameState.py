from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import List, Optional

from Boards import CheckerBoard, TicTacToeBoard, Connect4Board
from Player import Player
from flask import jsonify, Response


@dataclass
class GameState:
    board: [CheckerBoard | TicTacToeBoard | Connect4Board]
    players: List[Player]
    last_player: Optional[Player]
    last_move: int = -1
    status: str = ''
    game_over: bool = False

    def __repr__(self) -> str:
        return f'GameState(board={self.board}, players={self.players}, last_player={self.last_player}, ' \
               f'last_move={self.last_move}, status={self.status})'

    # def serialize(self):
    #     return json.dumps({
    #         "board": self.board,
    #         "players": self.players,
    #         "last_player": self.last_player,
    #         "last_move": self.last_move,
    #         "status": self.status,
    #         "game_over": self.game_over
    #     })

    @property
    def to_json(self) -> str:
        winner: Optional[str] = self.board.check_winner
        # next_player_id: int = (self.last_player.id + 1) % len(self.players)
        status: str = f"Game Over - It is a Draw!" if winner == 'Draw' else f"Game Over - Player {winner} wins" if winner \
            else f'{self.last_player.type} {self.last_player.color} on position {self.last_move}'
        state = {
            "squares": [piece for row in self.board.board for piece in row],
            "nextPlayer": self.last_player.to_json,
            "gameOver": winner is not None,
            "status": status,
            "numPlayers": len(self.players),
            "winner": winner
        }
        return json.dumps(state)  # Convert to dictionary and then to JSON string
        # return jsonify(state)
