"""
db.py
Database management for P2P Notes App.
Contains DatabaseManager for all SQLite operations.
"""

import sqlite3
import threading
from models import Note

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db_lock = threading.Lock()
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB init error: {e}")

    def load_notes(self):
        notes = {}
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.execute('SELECT id, content, updated_at FROM notes')
            for row in cursor:
                note = Note(row[0], row[1], row[2])
                notes[note.id] = note
            conn.close()
        except Exception as e:
            print(f"DB load error: {e}")
        return notes

    def save_note(self, note: Note):
        with self.db_lock:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.execute(
                    'INSERT OR REPLACE INTO notes (id, content, updated_at) VALUES (?, ?, ?)',
                    (note.id, note.content, note.updated_at)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"DB save error: {e}")

    def delete_note(self, note_id: str):
        with self.db_lock:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"DB delete error: {e}")