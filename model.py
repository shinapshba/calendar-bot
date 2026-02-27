import sqlite3

__DATABASE_FILE = 'database.db'

__SELECT_TOKEN = 'select token from bot'
__UPSERT_CHAT = ('insert into chat values(chat_id, username, title) on conflict(chat_id) do update '
                 'set username=excluded.username, title=excluded.title')


def select_token():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: row[0]
        curr = conn.cursor()
        curr.execute(__SELECT_TOKEN)
        return curr.fetchone()


def upsert_chat(chat_id, username, title):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: row[0]
        curr = conn.cursor()
        curr.execute(__UPSERT_CHAT, (chat_id, username, title,))
