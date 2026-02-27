import sqlite3

__DATABASE_FILE = 'database.db'

__SELECT_TOKEN = 'SELECT token FROM bot'

def select_token():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: row[0]
        curr = conn.cursor()
        curr.execute(__SELECT_TOKEN)
        return curr.fetchone()
