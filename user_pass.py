#  storing the username and password in mysql and if the one get call data is coming from mysql and stored in redis cache if it is second get call data is coming from redis


from flask import Flask, request, jsonify
import mysql.connector
import redis
import hashlib
from cryptography.fernet import Fernet

app = Flask(__name__)

# MySQL Connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "redis_db"
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Redis Connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    )
""")
conn.commit()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generate a key for encryption and decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(password_encrypted):
    return cipher_suite.decrypt(password_encrypted.encode()).decode()


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    password_hash = hash_password(password)
    # password_hash = encrypt_password(password)

    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409


@app.route('/get-password/<username>', methods=['GET'])
def get_password(username):
    cached_password = redis_client.get(username)

    if cached_password:
        print("Cache hit")
        # cached_password = decrypt_password(cached_password)
        return jsonify({"username": username, "password_hash": cached_password, "source": "redis"}), 200

    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        password_hash = user[0]
        redis_client.set(username, password_hash, ex=120)  # Cache password for 2 minutes
        # password_hash = decrypt_password(password_hash)
        return jsonify({"username": username, "password_hash": password_hash, "source": "mysql"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
