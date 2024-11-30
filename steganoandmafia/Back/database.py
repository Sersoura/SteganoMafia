import sqlite3
from datetime import datetime, timedelta

# Connexion à la base de données SQLite (création si elle n'existe pas)
def connect_db():
    return sqlite3.connect('files.db')

# Fonction pour créer la table si elle n'existe pas
def create_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expiration_at DATETIME NOT NULL
            )
        ''')
        conn.commit()

# Fonction pour insérer un fichier dans la base de données
def insert_file(filename, filepath, expiration_in_days):
    expiration_at = datetime.now() + timedelta(days=expiration_in_days)
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (filename, filepath, expiration_at)
            VALUES (?, ?, ?)
        ''', (filename, filepath, expiration_at))
        conn.commit()

# Fonction pour récupérer tous les fichiers
def get_files():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files')
        return cursor.fetchall()

# Fonction pour supprimer les fichiers expirés
def delete_expired_files():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM files WHERE expiration_at < CURRENT_TIMESTAMP
        ''')
        conn.commit()
