from model.root import execute, fetchall, MEETING_BASE_COLS, build_placeholders_with_params
from dto import MeetingWeekly

__SELECT_MEETING_WEEKLY = 'SELECT * FROM meeting_weekly WHERE chat_id = ?'
__SELECT_MEETING_WEEKLY_BY_USERNAME = __SELECT_MEETING_WEEKLY + ' AND username = ?'
__DELETE_MEETING_WEEKLY = 'DELETE FROM meeting_weekly WHERE id = ?'
__SELECT_MEETING_WEEKLY_NOT_NOTIFIED = 'SELECT * from meeting_weekly WHERE is_notified = 0'
__UPDATE_MEETING_WEEKLY_NOTIFIED_FLAG = 'UPDATE meeting_weekly SET is_notified = 1 WHERE id = ?'
__BACKUP_MEETING_WEEKLY = 'UPDATE meeting_weekly SET is_notified = 0'
__INSERT_MEETING_WEEKLY = f'''INSERT INTO meeting_weekly ({MEETING_BASE_COLS}, day, time) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''


def insert_meeting_weekly(chat_id, chat_title, username, place, description, notify_lag_min, day, time):
    execute(__INSERT_MEETING_WEEKLY, (chat_id, chat_title, username, place, description, notify_lag_min,
                                      day, time,))


def select_meetings_weekly(chat_id):
    fetchall(__SELECT_MEETING_WEEKLY, MeetingWeekly.row_factory(), (chat_id,))


def select_meetings_weekly_by_username(chat_id, username):
    fetchall(__SELECT_MEETING_WEEKLY_BY_USERNAME, MeetingWeekly.row_factory(), (chat_id, username,))


def delete_meeting_weekly(id_):
    execute(__DELETE_MEETING_WEEKLY, (id_,))


def select_meetings_weekly_not_notified():
    fetchall(__SELECT_MEETING_WEEKLY_NOT_NOTIFIED, MeetingWeekly.row_factory())


def update_meetings_weekly(id_):
    execute(__UPDATE_MEETING_WEEKLY_NOTIFIED_FLAG, (id_,))


def backup_meetings_weekly():
    execute(__BACKUP_MEETING_WEEKLY)


def select_meetings_weekly_for_chats(chat_ides):
    placeholders, chat_ides = build_placeholders_with_params(chat_ides)
    query = f'SELECT * FROM meeting_weekly WHERE chat_id IN ({placeholders})'
    fetchall(query, MeetingWeekly.row_factory(), chat_ides)
