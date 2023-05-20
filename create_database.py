import os
import sqlite3 as sq


def create_db():
    """Создает папку data, создает база данных с таблицами."""
    path = os.path.dirname(os.path.abspath(__file__)) + r"\data"
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    path = os.path.dirname(os.path.abspath(__file__)) + r"\data\database.db"
    with sq.connect(path) as con:
        cur = con.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS processor(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        frequency INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS motherboard(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        socket TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS computer(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status INTEGER,
        proc_id INTEGER NOT NULL,
        moth_id INTEGER NOT NULL,
        FOREIGN KEY(proc_id) REFERENCES processor(id),
        FOREIGN KEY(moth_id) REFERENCES motherboard(id)
        );

        CREATE TABLE IF NOT EXISTS friend(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
        );

        CREATE TABLE IF NOT EXISTS friend_computers(
        friend_id INTEGER REFERENCES friend(id),
        comp_id INTEGER REFERENCES computer(id),
        CONSTRAINT friend_computers PRIMARY KEY (friend_id, comp_id)
        );
        """)
