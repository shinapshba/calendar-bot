import sqlite3

from dto import Chat

MEETING_BASE_COLS = 'chat_id, chat_title, username, place, description, notify_lag_min'

__DATABASE_FILE = 'database.db'
__SELECT_DAY_OFF = 'SELECT date FROM day_off'
__INSERT_DAY_OFF = 'INSERT INTO day_off VALUES (?)'
__DELETE_DAY_OFF = 'DELETE FROM day_off'
__SELECT_TOKEN = 'SELECT data FROM token'
__SELECT_PRODUCTION_CALENDAR_TOKEN = 'SELECT data FROM production_calendar_token'
__IS_SUPER_USER = 'SELECT COUNT(*) FROM super_user WHERE username=?'
__SELECT_ALL_CHATS = 'SELECT * FROM chat'
__UPSERT_CHAT = '''INSERT INTO chat(chat_id, username, title) VALUES(?, ?, ?) ON CONFLICT(chat_id) DO UPDATE SET 
username=excluded.username, title=excluded.title'''


def build_placeholders_with_params(ides):
    if not ides:
        return [], ""
    clean_ides = [str(id_) for id_ in ides]
    return ','.join(['?'] * len(clean_ides)), clean_ides


def execute(query, parameters=None):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        if parameters is not None:
            curr.execute(query, parameters)
        else:
            curr.execute(query)
        conn.commit()


def fetchall(query, row_factory, parameters=None):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = row_factory
        curr = conn.cursor()
        if parameters is not None:
            curr.execute(query, parameters)
        else:
            curr.execute(query)
        return curr.fetchall()


def fetchone(query, parameters=None):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        if parameters is not None:
            curr.execute(query, parameters)
        else:
            curr.execute(query)
        return curr.fetchone()[0]


def is_super_user(username):
    return fetchone(__IS_SUPER_USER, (username,)) > 0


def select_token():
    return fetchone(__SELECT_TOKEN)


def select_production_calendar_token():
    return fetchone(__SELECT_PRODUCTION_CALENDAR_TOKEN)


def upsert_chat(chat_id, username, title):
    execute(__UPSERT_CHAT, (chat_id, username, title,))


def select_all_chats():
    return fetchall(__SELECT_ALL_CHATS, lambda cursor, row: Chat(row[0], row[1], row[2]))

def is_day_off(day_date: str):
    days = select_day_off()
    return bool(days) and day_date in days

def select_day_off():
    return fetchall(__SELECT_DAY_OFF, lambda cursor, row: row[0])

def insert_day_off(day_date: str):
    execute(__INSERT_DAY_OFF, (day_date,))

def delete_day_off():
    execute(__DELETE_DAY_OFF)
