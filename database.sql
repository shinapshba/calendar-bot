PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: super_user
CREATE TABLE IF NOT EXISTS super_user (
    username TEXT NOT NULL,
    userid TEXT NOT NULL
);

-- Таблица: token
CREATE TABLE IF NOT EXISTS token (
    data TEXT NOT NULL
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;