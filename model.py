import sqlite3

from dto import Chat

__DATABASE_FILE = 'database.db'

__SELECT_TOKEN = 'select data from token'
__IS_SUPER_USER = 'select exists (select 1 from super_user where username=?)'
__SELECT_ALL_CHATS = 'select * from chat'
__UPSERT_CHAT = ('insert into chat(chat_id, username, title) values(?, ?, ?) on conflict(chat_id) do update '
                 'set username=excluded.username, title=excluded.title')


def is_super_user(username):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__IS_SUPER_USER, (username,))
        return bool(curr.fetchone())


def select_token():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: row[0]
        curr = conn.cursor()
        curr.execute(__SELECT_TOKEN)
        return curr.fetchone()


def upsert_chat(chat_id, username, title):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__UPSERT_CHAT, (chat_id, username, title,))


def select_all_chats():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: Chat(row[0], row[1], row[2])
        curr = conn.cursor()
        curr.execute(__SELECT_ALL_CHATS)
        return curr.fetchall()
