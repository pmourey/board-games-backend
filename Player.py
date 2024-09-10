from dataclasses import dataclass

from flask import json, jsonify


@dataclass
class Player:
    id: int
    type: str
    color: str

    @property
    def to_json(self) -> str:
        return json.dumps(self.__dict__)

if __name__ == "__main__":
    # Créer deux instances de la classe Player
    player1 = Player(1, 'Human', 'X')
    player2 = Player(2, 'Computer', 'O')

    # Accéder aux attributs des instances
    print(player1.type)  # Output: Human
    print(player2.color)  # Output: O
