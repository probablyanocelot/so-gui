"""
soGUI — Database Layer

Description:
    This module handles all core database functionality for soGUI.
    It is responsible for creating the SQLite database, building
    every required table, and providing helper functions that the
    rest of the application can rely on.

    The purpose of this file is to keep database logic centralized
    and consistent, so the UI and service layers do not need to
    worry about SQL details. Any operation that requires reading
    or writing data—such as user authentication, asset lookups,
    checkouts, reservations, and audit logging—ultimately routes
    through this module.

    By keeping the database setup and utilities here, the rest of
    the application stays cleaner, easier to maintain, and more
    predictable across different environments (Windows vs macOS).
"""
import sqlite3
from pathlib import Path
from datetime import datetime   #import libraries

DB_PATH = Path("cams.db")   #define path so program can find databse

"""This function opens a connection to the soGUI SQLite database and 
turns on row_factory so query results can be accessed like dictionaries 
(for example, row["FIRST_NAME"]). It keeps all database connections 
consistent and makes the rest of the code easier to read."""
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

#This function sets up the entire database schema for soGUI. 
#It creates every table the system needs if they don’t already exist, 
#so it can safely be called at startup without wiping any existing data.
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    #Each commented section maps to a table group
    #
    #The User table stores employees and admins who log into soGUI, 
    # including their name, email, role, and password. It’s the core 
    # table for authentication and for tracking which employee performed an action.
    #
    #The Customers table tracks people who actually check out assets, separate 
    # from employees. It stores their email, name, and phone number so I can link 
    # checkouts and reservations back to a specific customer.
    #
    #The lookup tables define valid sites, locations, departments, and categories 
    # that assets can belong to. Keeping these in separate tables makes the data 
    # cleaner, prevents typos, and makes it easier to reuse the same values 
    # across many assets.
    #
    #The Asset table represents each inventory item in soGUI, including its ID, 
    # description, brand, model, cost, and where it lives (site, location, 
    # department, and category). It also tracks whether the asset is currently 
    # available and can optionally store a path to an image for that item.
    #
    #The Checkout table records every time an asset is checked out and returned. 
    # It links a customer to an asset with check-out time, optional check-in time, 
    # and an optional due date so I can build a full history of who used what and when.
    #
    #The Reservation table lets employees reserve assets ahead of time. 
    # It stores which asset is requested, who asked for it, who it is reserved for, 
    # the target date, and a simple status field so we can tell if a reservation 
    # is active, fulfilled, or cancelled.
    #
    #The Policy table gives soGUI a simple place to store text-based policy 
    # information, such as borrowing rules or usage guidelines. It’s intentionally 
    # small but can be expanded later if the policy system needs to grow.
    #
    #The AuditLog table keeps a running record of important actions in the system, 
    # such as changes to assets or checkouts. It stores which asset and employee 
    # were involved, what happened, when it happened, and any extra details 
    # for later review.
    cur.executescript("""
    -- ======================
    -- User (employees/admins)
    -- ======================
    CREATE TABLE IF NOT EXISTS User (
        EMP_ID      TEXT PRIMARY KEY,
        FIRST_NAME  TEXT NOT NULL,
        LAST_NAME   TEXT NOT NULL,
        EMAIL       TEXT,
        TITLE       TEXT,
        ROLE        TEXT NOT NULL,      -- 'admin' or 'standard'
        PASSWORD    TEXT                -- for class: plain text is OK
    );

    -- ======================
    -- Customers
    -- ======================
    CREATE TABLE IF NOT EXISTS Customers (
        CUST_EMAIL  TEXT PRIMARY KEY,
        FIRST_NAME  TEXT NOT NULL,
        LAST_NAME   TEXT NOT NULL,
        PHONE       TEXT
    );

    -- ======================
    -- Site / Location / Department / Category lookups
    -- ======================
    CREATE TABLE IF NOT EXISTS Site (
        SITE_ID     INTEGER PRIMARY KEY AUTOINCREMENT,
        SITE_NAME   TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Location (
        LOCATION_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
        LOCATION_NAME TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Department (
        DEPT_ID    INTEGER PRIMARY KEY AUTOINCREMENT,
        DEPT_NAME  TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Category (
        CATEGORY_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
        CATEGORY_NAME TEXT NOT NULL UNIQUE
    );

    -- ======================
    -- Asset (inventory items)
    -- ======================
    CREATE TABLE IF NOT EXISTS Asset (
        ASSET_ID        TEXT PRIMARY KEY,
        DESCRIPTION     TEXT,
        BRAND           TEXT,
        MODEL           TEXT,
        SERIAL          TEXT,
        PURCHASE_DATE   TEXT,     -- ISO datetime or just date string
        COST            REAL,
        SITE_NAME       TEXT,
        LOCATION_NAME   TEXT,
        DEPT_NAME       TEXT,
        CATEGORY_NAME   TEXT,
        FUNDING_SOURCE  TEXT,     -- optional text field for where the money came from
        QUANTITY        INTEGER,
        WARRANTY_INFO   TEXT,     -- optional text field for warranty details
        IMAGE_PATH      TEXT,     -- optional path to an image for this asset
        AVAILABLE       INTEGER NOT NULL DEFAULT 1,  -- 1=true, 0=false

        FOREIGN KEY (SITE_NAME)      REFERENCES Site(SITE_NAME),
        FOREIGN KEY (LOCATION_NAME)  REFERENCES Location(LOCATION_NAME),
        FOREIGN KEY (DEPT_NAME)      REFERENCES Department(DEPT_NAME),
        FOREIGN KEY (CATEGORY_NAME)  REFERENCES Category(CATEGORY_NAME)
    );

    -- ======================
    -- Checkout history
    -- ======================
    CREATE TABLE IF NOT EXISTS Checkout (
        TRANSACTION_NO  INTEGER PRIMARY KEY AUTOINCREMENT,
        CUST_EMAIL      TEXT NOT NULL,
        ASSET_ID        TEXT NOT NULL,
        CHECK_OUT       TEXT NOT NULL,   -- datetime out
        CHECK_IN        TEXT,            -- datetime in (NULL until returned)
        DUE_DATE        TEXT,            -- optional datetime due

        FOREIGN KEY (CUST_EMAIL) REFERENCES Customers(CUST_EMAIL),
        FOREIGN KEY (ASSET_ID)   REFERENCES Asset(ASSET_ID)
    );

    -- ======================
    -- Reservations (new design)
    -- ======================
    CREATE TABLE IF NOT EXISTS Reservation (
        RES_NO       INTEGER PRIMARY KEY AUTOINCREMENT,
        ASSET_ID     TEXT NOT NULL,
        REQUESTED_BY INTEGER,           -- Employee in soGUI (User.EMP_ID)
        RESERVED_FOR TEXT NOT NULL,     -- Person/department who will use it
        TARGET_DATE  TEXT,              -- When they want it (optional)
        CREATED_AT   TEXT NOT NULL,     -- When the reservation was created
        STATUS       TEXT NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE, FULFILLED, CANCELLED

        FOREIGN KEY (ASSET_ID)     REFERENCES Asset(ASSET_ID),
        FOREIGN KEY (REQUESTED_BY) REFERENCES User(EMP_ID)
    );

    -- ======================
    -- Policy
    -- ======================
    CREATE TABLE IF NOT EXISTS Policy (
        POLICY_ID    INTEGER PRIMARY KEY AUTOINCREMENT,
        POLICY_ONE   TEXT,
        POLICY_TWO   TEXT,
        POLICY_THREE TEXT
    );

    -- ======================
    -- Audit Log
    -- ======================
    CREATE TABLE IF NOT EXISTS AuditLog (
        LOG_NO    INTEGER PRIMARY KEY AUTOINCREMENT,
        ASSET_ID  TEXT,
        EMP_ID    TEXT,
        LOG_DATE  TEXT NOT NULL,
        ACTION    TEXT,
        DETAILS   TEXT,

        FOREIGN KEY (ASSET_ID) REFERENCES Asset(ASSET_ID),
        FOREIGN KEY (EMP_ID)   REFERENCES User(EMP_ID)
    );
    """)

    conn.commit()
    conn.close()

#This function writes a new row into the AuditLog table whenever the app needs 
# to record an action. It captures the employee ID, optional asset ID, a timestamp, 
# a short action label, and any details so we have a clear trail of what 
# the system has done.
def log_action(emp_id, action, asset_id=None, details=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO AuditLog (ASSET_ID, EMP_ID, LOG_DATE, ACTION, DETAILS)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            asset_id,
            emp_id,
            datetime.now().isoformat(timespec="seconds"),
            action,
            details,
        ),
    )
    conn.commit()
    conn.close()

