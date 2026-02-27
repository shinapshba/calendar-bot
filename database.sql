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

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;