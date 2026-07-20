import sqlite3

from dto import Chat, SentNotify

MEETING_BASE_COLS = 'chat_id, chat_title, username, place, description, notify_lag_min'

__DATABASE_FILE = 'database.db'
__SELECT_TOKEN = 'SELECT data FROM token'
__SELECT_PRODUCTION_CALENDAR_TOKEN = 'SELECT data FROM production_calendar_token'
__IS_SUPER_USER = 'SELECT COUNT(*) FROM super_user WHERE username=?'
__SELECT_ALL_CHATS = 'SELECT * FROM chat'
__SELECT_SENT_NOTIFY = 'SELECT * FROM sent_notify'
__SELECT_SENT_NOTIFY_BY_CHAT_ID = 'SELECT * FROM sent_notify WHERE chat_id = ?'
__INSERT_SENT_NOTIFY = 'INSERT INTO sent_notify VALUES(?, ?)'
__DELETE_SENT_NOTIFY = 'DELETE FROM sent_notify'
__DELETE_SENT_NOTIFY_BY_CHAT = 'DELETE FROM sent_notify WHERE chat_id = ?'
__DELETE_SENT_NOTIFY_BY_CHAT_AND_MESSAGE = 'DELETE FROM sent_notify WHERE chat_id = ? AND message_id = ?'
__SELECT_IS_TODAY_DAY_OFF = 'SELECT * FROM is_today_day_off'
__UPDATE_IS_TODAY_DAY_OFF = 'UPDATE is_today_day_off SET value = ?'
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


def select_sent_notify():
    return fetchall(__SELECT_SENT_NOTIFY, SentNotify.row_factory())

def select_sent_notify_by_chat_id(chat_id):
    return fetchall(__SELECT_SENT_NOTIFY_BY_CHAT_ID, SentNotify.row_factory(), (chat_id,))

def insert_sent_notify(chat_id, message_id):
    execute(__INSERT_SENT_NOTIFY, (chat_id, message_id,))

def delete_sent_notify():
    execute(__DELETE_SENT_NOTIFY)

def delete_sent_notify_by_chat_id(chat_id):
    execute(__DELETE_SENT_NOTIFY_BY_CHAT, (chat_id,))

def delete_sent_notify_by_chat_id_and_message_id(chat_id, message_id):
    execute(__DELETE_SENT_NOTIFY_BY_CHAT_AND_MESSAGE, (chat_id, message_id,))

def select_is_today_day_off():
    return bool(fetchone(__SELECT_IS_TODAY_DAY_OFF))

def update_is_today_day_off(is_day_off: bool):
    execute(__UPDATE_IS_TODAY_DAY_OFF, (int(is_day_off),))
