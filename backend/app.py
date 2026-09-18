import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from prometheus_flask_exporter import PrometheusMetrics



app = Flask(__name__)
CORS(app)

# Initialize Prometheus metrics (automatically sets up /metrics route)
metrics = PrometheusMetrics(app)

# Static metric info (optional, useful for dashboards)
metrics.info('app_info', 'Application info', version='1.0.0')

# ... your existing routes (/users, DB handlers, etc.) ...



DB_PATH = '/app/data/database.db'

# Consolidated database initialization logic
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
    ''')
    
    # Check if empty to prevent duplicating the sample data on every restart
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');")
        
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Run it immediately when the app starts
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Backend is running and connected to SQLite!"})

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users;').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in users])

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO users (name, email) VALUES (?, ?);', (name, email))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"}), 201

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?;', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"}), 200

@app.route('/status')
def status_check():
    return jsonify({"status": "healthy"}), 200

# your existing database and API routes ...



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

    