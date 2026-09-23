from model.root import execute, fetchall, MEETING_BASE_COLS, build_placeholders_with_params
from dto import MeetingWeeklyDouble

__SELECT_MEETING_WEEKLY_DOUBLE = 'SELECT * FROM meeting_weekly_double WHERE chat_id = ?'
__SELECT_MEETING_WEEKLY_DOUBLE_BY_USERNAME = __SELECT_MEETING_WEEKLY_DOUBLE + ' AND username = ?'
__DELETE_MEETING_WEEKLY_DOUBLE = 'DELETE FROM meeting_weekly_double WHERE id = ?'
__SELECT_MEETING_WEEKLY_DOUBLE_NOT_NOTIFIED = 'SELECT * from meeting_weekly_double WHERE is_notified = 0'
__UPDATE_MEETING_WEEKLY_DOUBLE_NOTIFIED_FLAG = 'UPDATE meeting_weekly_double SET is_notified = 1 WHERE id = ?'
__BACKUP_MEETING_WEEKLY_DOUBLE = 'UPDATE meeting_weekly_double SET is_notified = 0'
__SELECT_MEETING_WEEKLY_DOUBLE_BY_ID = 'SELECT * FROM meeting_weekly_double WHERE id = ?'
__INSERT_MEETING_WEEKLY_DOUBLE = f'''INSERT INTO meeting_weekly_double ({MEETING_BASE_COLS}, period, day, time) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''


def insert_meeting_weekly_double(chat_id, chat_title, username, place, description, notify_lag_min, period, day, time):
    execute(__INSERT_MEETING_WEEKLY_DOUBLE, (chat_id, chat_title, username, place, description,
                                             notify_lag_min, period, day, time,))


def select_meetings_weekly_double(chat_id):
    return fetchall(__SELECT_MEETING_WEEKLY_DOUBLE, MeetingWeeklyDouble.row_factory(), (chat_id,))


def select_meetings_weekly_double_by_username(chat_id, username):
    return fetchall(__SELECT_MEETING_WEEKLY_DOUBLE_BY_USERNAME, MeetingWeeklyDouble.row_factory(),
             (chat_id, username,))


def delete_meeting_weekly_double(id_):
    execute(__DELETE_MEETING_WEEKLY_DOUBLE, (id_,))


def select_meetings_weekly_double_not_notified():
    return fetchall(__SELECT_MEETING_WEEKLY_DOUBLE_NOT_NOTIFIED, MeetingWeeklyDouble.row_factory())


def update_meetings_weekly_double(id_):
    execute(__UPDATE_MEETING_WEEKLY_DOUBLE_NOTIFIED_FLAG, (id_,))


def backup_meetings_weekly_double():
    execute(__BACKUP_MEETING_WEEKLY_DOUBLE)


def select_meetings_weekly_double_for_chats(chat_ides):
    placeholders, chat_ides = build_placeholders_with_params(chat_ides)
    query = f'SELECT * FROM meeting_weekly_double WHERE chat_id IN ({placeholders})'
    return fetchall(query, MeetingWeeklyDouble.row_factory(), chat_ides)

def select_meeting_by_id(meeting_weekly_double_id):
    return fetchall(__SELECT_MEETING_WEEKLY_DOUBLE_BY_ID, MeetingWeeklyDouble.row_factory(),
                    (meeting_weekly_double_id,))[0]
