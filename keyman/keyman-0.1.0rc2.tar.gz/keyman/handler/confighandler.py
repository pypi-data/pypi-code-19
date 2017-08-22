import os
import sqlite3

from keyman.config import LOCAL_DIR, DB_PATH


def init_local_dir():
    if os.path.exists(DB_PATH):
        return sqlite3.connect(DB_PATH)
    else:  # db file or LOCAL_DIR doesn't exist.
        print("No local database found.", end=" ")
        # in case LOCAL_DIR doesn't exist
        os.makedirs(LOCAL_DIR, exist_ok=True)

        try:
            conn = sqlite3.connect(DB_PATH)
            print("A new database is created at " + DB_PATH + ". \n" +
                  "You can move/copy/remove it on your own.")
        except:
            print("Unable to create new database!")
            return None

        cursor = conn.cursor()
        # the creation order corresponds to the order of
        # keyman.entities.Account.keys
        cursor.execute(r"""
            CREATE TABLE Account (
            id INTEGER NOT NULL,
            title TEXT NOT NULL,
            username TEXT,
            description TEXT,
            password TEXT,
            phone TEXT,
            email TEXT,
            secret TEXT,
            deleted INTEGER DEFAULT 0,
            create_date TEXT,
            last_update TEXT,
            PRIMARY KEY (Id)
        )""")

        cursor.close()
        conn.commit()

        return conn


if __name__ == "__main__":
    init_local_dir()
