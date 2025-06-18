import sqlite3, os, base64
from datetime import datetime

DB_PATH = os.path.join("data", "vault.db")

class DatabaseManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    #schema
    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    title         TEXT NOT NULL,
                    username      TEXT NOT NULL,
                    password      TEXT NOT NULL,
                    notes         TEXT,
                    date_created  TEXT,
                    last_modified TEXT
                )
            """)

    # helpers
    @staticmethod
    def _to_b64(value):
        """Ensure value is a base-64 text string (never raw bytes)."""
        if isinstance(value, (bytes, bytearray)):
            return base64.b64encode(value).decode()
        return value

    # CRUD Fucntions
    def add_credential(self, title, username, encrypted_pw, notes=""):
        encrypted_pw = self._to_b64(encrypted_pw)
        now = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
                INSERT INTO credentials
                       (title, username, password, notes, date_created, last_modified)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, username, encrypted_pw, notes, now, now))

    def get_all_credentials(self):
        with self.conn:
            rows = self.conn.execute("SELECT * FROM credentials").fetchall()
            return [dict(r) for r in rows]

    def delete_credential(self, cred_id):
        with self.conn:
            self.conn.execute("DELETE FROM credentials WHERE id = ?", (cred_id,))

    def update_credential(self, cred_id, title, username, encrypted_pw, notes=""):
        encrypted_pw = self._to_b64(encrypted_pw)
        now = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
                UPDATE credentials
                   SET title        = ?, 
                       username     = ?, 
                       password     = ?, 
                       notes        = ?, 
                       last_modified= ?
                 WHERE id = ?
            """, (title, username, encrypted_pw, notes, now, cred_id))

    def close(self):
        self.conn.close()
