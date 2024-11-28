from flask import Flask, request, jsonify
import psycopg2
import os
import requests

app = Flask(__name__)

# Set up environment variables
SERVER_ID = os.environ.get("SHARD_ID", 1)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create a connection to the PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Shard computation based on `User-ID mod 3`
def get_shard_id(user_id):
    return user_id % 3 + 1

# Index route to confirm server ID
@app.route('/')
def index():
    return f"Flask Server {SERVER_ID}"

# Route to handle money requests
@app.route('/send_money', methods=['POST'])
def send_money():
    data = request.get_json()
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    amount = data.get('amount')

    if not all([sender_id, recipient_id, amount]):
        return jsonify({"error": "Missing data"}), 400

    # Determine which shard the recipient belongs to
    recipient_shard_id = get_shard_id(recipient_id)

    if recipient_shard_id == int(SERVER_ID):
        # Save to the local database if the recipient is on this shard
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO requests (sender_id, recipient_id, amount) VALUES (%s, %s, %s)",
                    (sender_id, recipient_id, amount))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Money request saved on shard {SERVER_ID}"}), 200
    else:
        # Forward the request to the correct shard
        target_url = f"http://flask{recipient_shard_id}:500{recipient_shard_id}/send_money"
        response = requests.post(target_url, json=data)
        return jsonify({"message": f"Request forwarded to shard {recipient_shard_id}"}), response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("FLASK_RUN_PORT", 5000)))
