### Game board's arena using React (for Front-end) and Flask (for Back-end)

#### [Front-end: React JS (for the game)](https://github.com/pmourey/tic-tac-toe-app)
#### Back-end: Flask (to manage game state)

Endpoint accessible here: http://philippe.mourey.com:1999

- Todos:
  - [x] Implement Tic Tac Toe game with one player
  - [x] Add Connect 4 game
  - [x] Implement game with 2 players (player + computer)
  - [ ] Implement game with 2 player (computer + computer)s
  - [ ] Create official certificate with Let's Encrypt or use pythonAnywhere certificate


### Setup instructions
  - Clôner le dépot via GIT:
    - `git clone https://github.com/pmourey/tic-tac-toe-backend.git`
  - Aller dans le répertoire du projet:
    - `cd tic-tac-toe-backend`
  - Créer l'environnement virtuel (avec la version active de python,ou toute autre version de python correctement installée incluant TCL/TK))
    - `python -m venv ENV`
  - Charger l'environnement virtuel:
    - `source ENV/Scripts/activate` (sous Git Bash)
    - `source ENV/Scripts/activate.ps1` (sous Power shell)
    - `source ENV/Scripts/activate.bat` (sous Command Prompt)
  - Mettre à jour la version de pip
    - `python -m pip install --upgrade pip`
  - Installer les modules du projet:
    - `pip install -r requirements.txt`

### Run instructions
- Lancer Flask:
  - `python flask_app.py`
    
