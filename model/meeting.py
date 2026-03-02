from model.root import execute, fetchall, MEETING_BASE_COLS, build_placeholders_with_params
from dto import Meeting

__INSERT_MEETING = f'INSERT INTO meeting ({MEETING_BASE_COLS}, date_time) VALUES (?, ?, ?, ?, ?, ?, ?)'
__SELECT_MEETING = 'SELECT * FROM meeting WHERE chat_id = ?'
__DELETE_MEETING = 'DELETE FROM meeting WHERE id = ?'
__SELECT_MEETING_BY_USERNAME = __SELECT_MEETING + ' AND username = ?'
__SELECT_MEETING_FOR_NOTIFY_DAY = 'SELECT * FROM meeting WHERE is_notified_day = 0'
__SELECT_MEETING_FOR_NOTIFY_MIN = 'SELECT * FROM meeting WHERE is_notified_min = 0'
__UPDATE_MEETING_NOTIFY_DAY = 'UPDATE meeting SET is_notified_day = 1 WHERE id = ?'
__UPDATE_MEETING_NOTIFY_MIN = 'UPDATE meeting SET is_notified_min = 1 WHERE id = ?'


def insert_meeting(chat_id, chat_title, username, place, description, notify_lag_min, date_time):
    execute(__INSERT_MEETING, (chat_id, chat_title, username, place, description, notify_lag_min, date_time,))


def select_meetings(chat_id):
    return fetchall(__SELECT_MEETING, Meeting.row_factory(), (chat_id,))


def select_meetings_by_username(chat_id, username):
    return fetchall(__SELECT_MEETING, Meeting.row_factory(), (chat_id, username,))


def delete_meeting(id_):
    execute(__DELETE_MEETING, (id_,))


def select_meetings_for_notify_by_day():
    return fetchall(__SELECT_MEETING_FOR_NOTIFY_DAY, Meeting.row_factory())


def select_meetings_for_notify_by_min():
    return fetchall(__SELECT_MEETING_FOR_NOTIFY_MIN, Meeting.row_factory())


def update_meeting_notify_flag_day(id_):
    execute(__UPDATE_MEETING_NOTIFY_DAY, (id_,))


def update_meeting_notify_flag_min(id_):
    execute(__UPDATE_MEETING_NOTIFY_MIN, (id_,))


def select_meetings_for_chats(chat_ides):
    placeholders, chat_ides = build_placeholders_with_params(chat_ides)
    query = f'SELECT * FROM meeting WHERE chat_id IN ({placeholders})'
    return fetchall(query, Meeting.row_factory(), chat_ides)
