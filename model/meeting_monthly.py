from model.root import execute, fetchall, MEETING_BASE_COLS, build_placeholders_with_params
from dto import MeetingMonthly

__SELECT_MEETING_MONTHLY = 'SELECT * FROM meeting_monthly WHERE chat_id = ?'
__DELETE_MEETING_MONTHLY = 'DELETE FROM meeting_monthly WHERE id = ?'
__SELECT_MEETING_MONTHLY_BY_USERNAME = __SELECT_MEETING_MONTHLY + ' AND username = ?'
__SELECT_MEETING_MONTHLY_NOT_NOTIFIED = 'SELECT * from meeting_monthly WHERE is_notified = 0'
__UPDATE_MEETING_MONTHLY_NOTIFIED_FLAG = 'UPDATE meeting_monthly SET is_notified = 1 WHERE id = ?'
__BACKUP_MEETING_MONTHLY = 'UPDATE meeting_monthly SET is_notified = 0'
__INSERT_MEETING_MONTHLY = f'''INSERT INTO meeting_monthly ({MEETING_BASE_COLS}, day_of_month, time) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''


def select_meetings_monthly(chat_id):
    return fetchall(__SELECT_MEETING_MONTHLY, MeetingMonthly.row_factory(), (chat_id,))


def insert_meeting_monthly(chat_id, chat_title, username, place, description, notify_lag_min, day_of_month, time):
    execute(__INSERT_MEETING_MONTHLY, (chat_id, chat_title, username, place, description, notify_lag_min,
                                       day_of_month, time,))


def select_meetings_monthly_for_chats(chat_ides):
    placeholders, chat_ides = build_placeholders_with_params(chat_ides)
    query = f'SELECT * FROM meeting_monthly WHERE chat_id IN ({placeholders})'
    return fetchall(query, MeetingMonthly.row_factory(), chat_ides)


def select_meetings_monthly_by_username(chat_id, username):
    return fetchall(__SELECT_MEETING_MONTHLY_BY_USERNAME, MeetingMonthly.row_factory(), (chat_id, username,))


def delete_meeting_monthly(id_):
    execute(__DELETE_MEETING_MONTHLY, (id_,))


def select_meetings_monthly_not_notified():
    return fetchall(__SELECT_MEETING_MONTHLY_NOT_NOTIFIED, MeetingMonthly.row_factory())


def update_meetings_monthly(id_):
    execute(__UPDATE_MEETING_MONTHLY_NOTIFIED_FLAG, (id_,))


def backup_meetings_monthly():
    execute(__BACKUP_MEETING_MONTHLY)
