from model.root import execute, fetchall, MEETING_BASE_COLS, build_placeholders_with_params
from dto import MeetingDaily

__SELECT_MEETING_DAILY = 'SELECT * FROM meeting_daily WHERE chat_id = ?'
__DELETE_MEETING_DAILY = 'DELETE FROM meeting_daily WHERE id = ?'
__SELECT_MEETING_DAILY_BY_USERNAME = __SELECT_MEETING_DAILY + ' AND username = ?'
__INSERT_MEETING_DAILY = f'INSERT INTO meeting_daily ({MEETING_BASE_COLS}, time) VALUES (?, ?, ?, ?, ?, ?, ?)'
__SELECT_MEETING_DAILY_NOT_NOTIFIED = 'SELECT * from meeting_daily WHERE is_notified = 0'
__UPDATE_MEETING_DAILY_NOTIFIED_FLAG = 'UPDATE meeting_daily SET is_notified = 1 WHERE id = ?'
__BACKUP_MEETING_DAILY = 'UPDATE meeting_daily SET is_notified = 0'
__SELECT_MEETING_DAILY_BY_ID = 'SELECT * FROM meeting_daily WHERE id = ?'


def select_meetings_daily(chat_id):
    return fetchall(__SELECT_MEETING_DAILY, MeetingDaily.row_factory(), (chat_id,))


def select_meetings_daily_by_username(chat_id, username):
    return fetchall(__SELECT_MEETING_DAILY_BY_USERNAME, MeetingDaily.row_factory(), (chat_id, username,))


def delete_meeting_daily(id_):
    execute(__DELETE_MEETING_DAILY, (id_,))


def insert_meeting_daily(chat_id, chat_title, username, place, description, notify_lag_min, time):
    execute(__INSERT_MEETING_DAILY, (chat_id, chat_title, username, place, description,
                                     notify_lag_min, time,))


def select_meetings_daily_not_notified():
    return fetchall(__SELECT_MEETING_DAILY_NOT_NOTIFIED, MeetingDaily.row_factory())


def update_meetings_daily(id_):
    execute(__UPDATE_MEETING_DAILY_NOTIFIED_FLAG, (id_,))


def backup_meetings_daily():
    execute(__BACKUP_MEETING_DAILY)


def select_meetings_daily_for_chats(chat_ides):
    placeholders, chat_ides = build_placeholders_with_params(chat_ides)
    query = f'SELECT * FROM meeting_daily WHERE chat_id IN ({placeholders})'
    return fetchall(query, MeetingDaily.row_factory(), chat_ides)


def select_meeting_by_id(meeting_daily_id):
    return fetchall(__SELECT_MEETING_DAILY_BY_ID, MeetingDaily.row_factory(), (meeting_daily_id,))[0]
