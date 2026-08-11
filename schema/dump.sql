PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS super_user (
    username    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS token (
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proxy (
    data TEXT NOT NULL
);

CREATE TABLE production_calendar_token (
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat (
    chat_id     TEXT NOT NULL UNIQUE,
    username    TEXT,
    title       TEXT
);

CREATE TABLE IF NOT EXISTS meeting (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id         TEXT    NOT NULL,
    chat_title      TEXT    NOT NULL,
    username        TEXT    NOT NULL,
    place           TEXT,
    description     TEXT,
    notify_lag_min  INTEGER NOT NULL,
    date_time       TEXT,
    is_notified_day INTEGER NOT NULL DEFAULT (0),
    is_notified_min INTEGER NOT NULL DEFAULT (0)
);

CREATE TABLE IF NOT EXISTS meeting_daily (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id        TEXT    NOT NULL,
    chat_title      TEXT    NOT NULL,
    username       TEXT    NOT NULL,
    place          TEXT,
    description    TEXT,
    notify_lag_min INTEGER NOT NULL,
    time           TEXT    NOT NULL,
    is_notified    INTEGER DEFAULT (0)
);

CREATE TABLE IF NOT EXISTS meeting_weekly (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id        TEXT    NOT NULL,
    chat_title     TEXT    NOT NULL,
    username       TEXT    NOT NULL,
    place          TEXT,
    description    TEXT,
    notify_lag_min INTEGER NOT NULL,
    day            INTEGER NOT NULL,
    time           TEXT    NOT NULL,
    is_notified    INTEGER DEFAULT (0)
);

CREATE TABLE IF NOT EXISTS meeting_weekly_double (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id        TEXT    NOT NULL,
    chat_title     TEXT    NOT NULL,
    username       TEXT    NOT NULL,
    place          TEXT,
    description    TEXT,
    notify_lag_min INTEGER NOT NULL,
    period         INTEGER NOT NULL,
    day            INTEGER NOT NULL,
    time           TEXT    NOT NULL,
    is_notified    INTEGER DEFAULT (0)
);

CREATE TABLE IF NOT EXISTS meeting_monthly (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id        TEXT    NOT NULL,
    chat_title     TEXT    NOT NULL,
    username       TEXT    NOT NULL,
    place          TEXT,
    description    TEXT,
    notify_lag_min INTEGER NOT NULL,
    day_of_month   INTEGER NOT NULL,
    time           TEXT    NOT NULL,
    is_notified    INTEGER DEFAULT (0)
);

CREATE TABLE sent_notify (
    chat_id    TEXT NOT NULL,
    message_id TEXT NOT NULL
);

CREATE TABLE is_today_day_off (
    value INTEGER NOT NULL DEFAULT (0)
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;