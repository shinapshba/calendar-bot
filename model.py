import sqlite3

from dto import Chat, Meeting, MeetingDaily, MeetingWeekly, MeetingWeeklyDouble

__DATABASE_FILE = 'database.db'

__SELECT_TOKEN = 'select data from token'
__IS_SUPER_USER = 'select exists (select 1 from super_user where username=?)'
__SELECT_ALL_CHATS = 'select * from chat'

__SELECT_MEETING = 'SELECT * FROM meeting WHERE chat_id = ?'
__SELECT_MEETING_DAILY = 'SELECT * FROM meeting_daily WHERE chat_id = ?'
__SELECT_MEETING_WEEKLY = 'SELECT * FROM meeting_weekly WHERE chat_id = ?'
__SELECT_MEETING_WEEKLY_DOUBLE = 'SELECT * FROM meeting_weekly_double WHERE chat_id = ?'
__SELECT_MEETING_DAILY_BY_USERNAME = __SELECT_MEETING_DAILY + ' AND username = ?'
__SELECT_MEETING_WEEKLY_BY_USERNAME = __SELECT_MEETING_WEEKLY + ' AND username = ?'
__SELECT_MEETING_WEEKLY_DOUBLE_BY_USERNAME = __SELECT_MEETING_WEEKLY_DOUBLE + ' AND username = ?'
__SELECT_MEETING_BY_USERNAME = __SELECT_MEETING + ' AND username = ?'

__DELETE_MEETING = 'DELETE FROM meeting WHERE id = ?'
__DELETE_MEETING_DAILY = 'DELETE FROM meeting_daily WHERE id = ?'
__DELETE_MEETING_WEEKLY = 'DELETE FROM meeting_weekly WHERE id = ?'
__DELETE_MEETING_WEEKLY_DOUBLE = 'DELETE FROM meeting_weekly_double WHERE id = ?'

__UPSERT_CHAT = ('insert into chat(chat_id, username, title) values(?, ?, ?) on conflict(chat_id) do update '
                 'set username=excluded.username, title=excluded.title')
__INSERT_MEETING_DAILY = ('INSERT INTO meeting_daily (chat_id, username, place, description, time, notify_lag_min) '
                          'VALUES (?, ?, ?, ?, ?, ?)')
__INSERT_MEETING_WEEKLY = ('INSERT INTO meeting_weekly ('
                           'chat_id, username, place, description, day, time, notify_lag_min'
                           ') VALUES (?, ?, ?, ?, ?, ?, ?)')
__INSERT_MEETING_WEEKLY_DOUBLE = ('INSERT INTO meeting_weekly_double ('
                                  'chat_id, username, place, description, is_even, day, time, notify_lag_min'
                                  ') VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
__INSERT_MEETING = ('INSERT INTO meeting (chat_id, username, place, description, date_time, notify_lag_min) '
                    'VALUES (?, ?, ?, ?, ?, ?)')

__SELECT_MEETING_DAILY_NOT_NOTIFIED = 'SELECT * from meeting_daily WHERE is_notified = 0'
__SELECT_MEETING_WEEKLY_NOT_NOTIFIED = 'SELECT * from meeting_weekly WHERE is_notified = 0'
__SELECT_MEETING_WEEKLY_DOUBLE_NOT_NOTIFIED = 'SELECT * from meeting_weekly_double WHERE is_notified = 0'
__SELECT_MEETING_FOR_NOTIFY_DAY = 'SELECT * FROM meeting WHERE is_notified_day = 0'
__SELECT_MEETING_FOR_NOTIFY_MIN = 'SELECT * FROM meeting WHERE is_notified_min = 0'
__UPDATE_MEETING_NOTIFY_DAY = 'UPDATE meeting SET is_notified_day = 1 WHERE id = ?'
__UPDATE_MEETING_NOTIFY_MIN = 'UPDATE meeting SET is_notified_min = 1 WHERE id = ?'
__UPDATE_MEETING_DAILY_NOTIFIED_FLAG = 'UPDATE meeting_daily SET is_notified = 1 WHERE id = ?'
__UPDATE_MEETING_WEEKLY_NOTIFIED_FLAG = 'UPDATE meeting_weekly SET is_notified = 1 WHERE id = ?'
__UPDATE_MEETING_WEEKLY_DOUBLE_NOTIFIED_FLAG = 'UPDATE meeting_weekly_double SET is_notified = 1 WHERE id = ?'
__BACKUP_MEETING_DAILY = 'UPDATE meeting_daily SET is_notified = 0'
__BACKUP_MEETING_WEEKLY = 'UPDATE meeting_weekly SET is_notified = 0'
__BACKUP_MEETING_WEEKLY_DOUBLE = 'UPDATE meeting_weekly_double SET is_notified = 0'


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


def insert_meeting(chat_id, username, place, description, date_time, notify_lag_min):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__INSERT_MEETING, (chat_id, username, place, description, date_time, notify_lag_min))
        conn.commit()


def insert_meeting_daily(chat_id, username, place, description, time, notify_lag_min):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__INSERT_MEETING_DAILY, (chat_id, username, place, description, time, notify_lag_min))
        conn.commit()


def insert_meeting_weekly(chat_id, username, place, description, day, time, notify_lag_min):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__INSERT_MEETING_WEEKLY, (chat_id, username, place, description, day, time,
                                               notify_lag_min,))
        conn.commit()


def insert_meeting_weekly_double(chat_id, username, place, description, period, day, time, notify_lag_min):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__INSERT_MEETING_WEEKLY_DOUBLE, (chat_id, username, place, description, period, day,
                                                      time, notify_lag_min,))
        conn.commit()


def select_meetings(chat_id):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: Meeting(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                                       row[8])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING, (chat_id,))
        return curr.fetchall()


def select_meetings_daily(chat_id):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingDaily(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                            row[7])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_DAILY, (chat_id,))
        return curr.fetchall()


def select_meetings_weekly(chat_id):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingWeekly(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                             row[7], row[8])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_WEEKLY, (chat_id,))
        return curr.fetchall()


def select_meetings_weekly_double(chat_id):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingWeeklyDouble(row[0], row[1], row[2], row[3], row[4], row[5],
                                                                   row[6], row[7], row[8], row[9])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_WEEKLY_DOUBLE, (chat_id,))
        return curr.fetchall()


def select_meetings_by_username(chat_id, username):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: Meeting(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                                       row[8])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_BY_USERNAME, (chat_id, username,))
        return curr.fetchall()


def select_meetings_daily_by_username(chat_id, username):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingDaily(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                            row[7])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_DAILY_BY_USERNAME, (chat_id, username,))
        return curr.fetchall()


def select_meetings_weekly_by_username(chat_id, username):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingWeekly(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                             row[7], row[8])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_WEEKLY_BY_USERNAME, (chat_id, username,))
        return curr.fetchall()


def select_meetings_weekly_double_by_username(chat_id, username):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingWeeklyDouble(row[0], row[1], row[2], row[3], row[4], row[5],
                                                                   row[6], row[7], row[8], row[9])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_WEEKLY_DOUBLE_BY_USERNAME, (chat_id, username,))
        return curr.fetchall()


def delete_meeting(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__DELETE_MEETING, (id_,))
        conn.commit()


def delete_meeting_daily(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__DELETE_MEETING_DAILY, (id_,))
        conn.commit()


def delete_meeting_weekly(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__DELETE_MEETING_WEEKLY, (id_,))
        conn.commit()


def delete_meeting_weekly_double(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__DELETE_MEETING_WEEKLY_DOUBLE, (id_,))
        conn.commit()


def select_meetings_daily_not_notified():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingDaily(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                            row[7])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_DAILY_NOT_NOTIFIED)
        return curr.fetchall()


def select_meetings_weekly_not_notified():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingWeekly(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                             row[7], row[8])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_WEEKLY_NOT_NOTIFIED)
        return curr.fetchall()


def select_meetings_weekly_double_not_notified():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: MeetingWeeklyDouble(row[0], row[1], row[2], row[3], row[4], row[5],
                                                                   row[6], row[7], row[8], row[9])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_WEEKLY_DOUBLE_NOT_NOTIFIED)
        return curr.fetchall()


def select_meetings_for_notify_by_day():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: Meeting(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                                       row[8])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_FOR_NOTIFY_DAY)
        return curr.fetchall()


def select_meetings_for_notify_by_min():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        conn.row_factory = lambda cursor, row: Meeting(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                                       row[8])
        curr = conn.cursor()
        curr.execute(__SELECT_MEETING_FOR_NOTIFY_MIN)
        return curr.fetchall()


def update_meetings_daily(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__UPDATE_MEETING_DAILY_NOTIFIED_FLAG, (id_,))
        conn.commit()


def update_meetings_weekly(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__UPDATE_MEETING_WEEKLY_NOTIFIED_FLAG, (id_,))
        conn.commit()


def update_meetings_weekly_double(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__UPDATE_MEETING_WEEKLY_DOUBLE_NOTIFIED_FLAG, (id_,))
        conn.commit()


def update_meeting_notify_flag_day(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__UPDATE_MEETING_NOTIFY_DAY, (id_,))
        conn.commit()


def update_meeting_notify_flag_min(id_):
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__UPDATE_MEETING_NOTIFY_MIN, (id_,))
        conn.commit()


def backup_meetings_daily():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__BACKUP_MEETING_DAILY)
        conn.commit()


def backup_meetings_weekly():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__BACKUP_MEETING_WEEKLY)
        conn.commit()


def backup_meetings_weekly_double():
    with sqlite3.connect(__DATABASE_FILE, check_same_thread=False) as conn:
        curr = conn.cursor()
        curr.execute(__BACKUP_MEETING_WEEKLY_DOUBLE)
        conn.commit()
