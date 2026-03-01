PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS super_user (
    username    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS token (
    data TEXT NOT NULL
);

CREATE TABLE chat (
    chat_id     TEXT NOT NULL UNIQUE,
    username    TEXT,
    title       TEXT
);

CREATE TABLE meeting (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id         TEXT    NOT NULL,
    chat_title      TEXT    NOT NULL,
    username        TEXT    NOT NULL,
    place           TEXT,
    description     TEXT,
    date_time       TEXT,
    notify_lag_min  INTEGER NOT NULL,
    is_notified_day INTEGER NOT NULL DEFAULT (0),
    is_notified_min INTEGER NOT NULL DEFAULT (0)
);

CREATE TABLE meeting_daily (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id        TEXT    NOT NULL,
    chat_title      TEXT    NOT NULL,
    username       TEXT    NOT NULL,
    place          TEXT,
    description    TEXT,
    time           TEXT    NOT NULL,
    notify_lag_min INTEGER NOT NULL,
    is_notified    INTEGER DEFAULT (0)
);

CREATE TABLE meeting_weekly (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id        TEXT    NOT NULL,
    chat_title     TEXT    NOT NULL,
    username       TEXT    NOT NULL,
    place          TEXT,
    description    TEXT,
    day            INTEGER NOT NULL,
    time           TEXT    NOT NULL,
    notify_lag_min INTEGER NOT NULL,
    is_notified    INTEGER DEFAULT (0)
);

CREATE TABLE meeting_weekly_double (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id        TEXT    NOT NULL,
    chat_title     TEXT    NOT NULL,
    username       TEXT    NOT NULL,
    place          TEXT,
    description    TEXT,
    period         INTEGER NOT NULL,
    day            INTEGER NOT NULL,
    time           TEXT    NOT NULL,
    notify_lag_min INTEGER NOT NULL,
    is_notified    INTEGER DEFAULT (0)
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;