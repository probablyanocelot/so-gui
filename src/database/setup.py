import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("sogui.db")   #define path so program can find databse

"""This function opens a connection to the soGUI SQLite database and 
turns on row_factory so query results can be accessed like dictionaries 
(for example, row["FIRST_NAME"]). It keeps all database connections 
consistent and makes the rest of the code easier to read."""
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn


def seed_default_admin():
    """
    Creates a default admin user if the User table is empty.
    This runs only once when the database is brand new.
    """

    conn = get_connection()
    cur = conn.cursor()

    # Check if ANY users exist
    cur.execute("SELECT COUNT(*) AS cnt FROM User")
    count = cur.fetchone()["cnt"]

    if count == 0:
        # Check if there any any users in database. If there are no users then
        # Insert a default system admin
        cur.execute(
            """
            INSERT INTO User (EMP_ID, FIRST_NAME, LAST_NAME, EMAIL, TITLE, ROLE, PASSWORD)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "admin",
                "System",
                "Admin",
                "admin@example.com",
                "Administrator",
                "admin",   #username
                "pswd",    #password
            ),
        )

        conn.commit()

    conn.close()

