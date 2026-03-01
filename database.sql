PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS super_user;
CREATE TABLE super_user (
    username    TEXT NOT NULL
);

DROP TABLE IF EXISTS token;
CREATE TABLE token (
    data TEXT NOT NULL
);

DROP TABLE IF EXISTS chat;
CREATE TABLE chat (
    chat_id     TEXT NOT NULL UNIQUE,
    username    TEXT,
    title       TEXT
);

DROP TABLE IF EXISTS meeting;
CREATE TABLE meeting (
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

DROP TABLE IF EXISTS meeting_daily;
CREATE TABLE meeting_daily (
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

DROP TABLE IF EXISTS meeting_weekly;
CREATE TABLE meeting_weekly (
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

DROP TABLE IF EXISTS meeting_weekly_double;
CREATE TABLE meeting_weekly_double (
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

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;