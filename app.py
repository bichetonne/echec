import os
import random
import libsql
import sqlite3
from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import chess
import chess.engine

app = Flask(__name__)
STOCKFISH_PATH = "stockfish"

TURSO_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

def get_db():
    if TURSO_URL:
        return libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
    else:
        return sqlite3.connect('biche_chess.db')

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            elo INTEGER DEFAULT 1200
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            result TEXT,
            moves TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()
    level = data.get('level', 'moyen')

    if not username or not password:
        return jsonify({"success": False, "message": "Nom d'utilisateur et mot de passe requis."}), 400

    elo_map = {
        'debutant': 800,
        'moyen': 1200,
        'pro': 1600
    }
    initial_elo = elo_map.get(level, 1200)
    hashed_password = generate_password_hash(password)

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, elo) VALUES (?, ?, ?)", (username, hashed_password, initial_elo))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Compte créé avec succès !", "elo": initial_elo})
    except Exception:
        return jsonify({"success": False, "message": "Ce nom d'utilisateur existe déjà."}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, elo FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        return jsonify({"success": True, "message": "Connexion réussie !", "username": username, "elo": user[2]})
    else:
        return jsonify({"success": False, "message": "Identifiants incorrects."}), 401

@app.route('/api/update_elo', methods=['POST'])
def update_elo():
    data = request.json
    username = data.get('username')
    new_elo = data.get('elo')

    if not username or new_elo is None:
        return jsonify({"success": False, "message": "Données invalides."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET elo = ? WHERE username = ?", (new_elo, username))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "elo": new_elo})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, elo FROM users ORDER BY elo DESC LIMIT 10")
    users = cursor.fetchall()
    conn.close()

    ranking = [{"username": u[0], "elo": u[1]} for u in users]
    return jsonify({"success": True, "leaderboard": ranking})

@app.route('/api/save_game', methods=['POST'])
def save_game():
    data = request.json
    username = data.get('username')
    result = data.get('result')
    moves = data.get('moves')

    if not username:
        return jsonify({"success": False}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO training_games (username, result, moves) VALUES (?, ?, ?)", (username, result, moves))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- ROUTE DU ROBOT AVEC SÉCURITÉ DE SECOURS ---
@app.route('/api/robot_move', methods=['POST'])
def robot_move():
    data = request.json
    fen = data.get('fen')
    skill_level = data.get('skill_level', 20)

    board = chess.Board(fen)

    try:
        # Tente d'utiliser Stockfish
        transport, engine = chess.engine.popen_uci(STOCKFISH_PATH)
        engine.configure({"Skill Level": skill_level})
        result = engine.play(board, chess.engine.Limit(time=0.5))
        engine.quit()
        return jsonify({"success": True, "move": result.move.uci()})
    except Exception:
        # MODE DE SECOURS : Si Stockfish échoue (ex: absent sur le cloud), python-chess joue un coup légal automatiquement
        legal_moves = list(board.legal_moves)
        if legal_moves:
            chosen_move = random.choice(legal_moves)
            return jsonify({"success": True, "move": chosen_move.uci()})
        return jsonify({"success": False, "message": "Aucun coup disponible"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)