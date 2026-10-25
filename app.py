from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import chess
import chess.engine

app = Flask(__name__)
STOCKFISH_PATH = "stockfish"

# --- BASE DE DONNÉES UTILISATEURS ---
def init_db():
    conn = sqlite3.connect('biche_chess.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
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

    if not username or not password:
        return jsonify({"success": False, "message": "Nom d'utilisateur et mot de passe requis."}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect('biche_chess.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Compte créé avec succès !"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Ce nom d'utilisateur existe déjà."}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()

    conn = sqlite3.connect('biche_chess.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        return jsonify({"success": True, "message": "Connexion réussie !", "username": username})
    else:
        return jsonify({"success": False, "message": "Identifiants incorrects."}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)