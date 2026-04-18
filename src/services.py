"""
soGUI — Service Layer

Description:
    This file contains all core database-facing logic for soGUI.
    These functions act as the “middle layer” between the UI and
    the database, handling users, customers, assets, checkouts,
    maintenance logs, and audit records.

    The overall goal here is to keep the UI code clean by putting
    anything data-related into this module instead.
"""

from datetime import datetime
from db import get_connection, log_action


# ================================================================
# USER MANAGEMENT
# ================================================================

from db import get_connection
from datetime import datetime

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


#Create a new employee record in the User table.
#acting_emp_id is used for audit logging if another user performs the action.
    
def create_employee(emp_id, first_name, last_name,
                    email=None, title=None, role="standard",
                    password=None, acting_emp_id=None):
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO User (EMP_ID, FIRST_NAME, LAST_NAME, EMAIL, TITLE, ROLE, PASSWORD)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (emp_id, first_name, last_name, email, title, role, password),
    )
    conn.commit()
    conn.close()

    # Log who created the employee account
    if acting_emp_id:
        log_action(acting_emp_id, "CREATE_EMPLOYEE", details=f"Created {emp_id}")
    return emp_id


#Return all employees sorted alphabetically.
def get_employees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM User ORDER BY LAST_NAME, FIRST_NAME")
    rows = cur.fetchall()
    conn.close()
    return rows


def update_employee(emp_id, first_name, last_name,
                    email=None, title=None, role="standard",
                    acting_emp_id=None):
    """
    Update an employee’s basic info (does not update password).
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE User
        SET FIRST_NAME = ?,
            LAST_NAME  = ?,
            EMAIL      = ?,
            TITLE      = ?,
            ROLE       = ?
        WHERE EMP_ID   = ?
        """,
        (first_name, last_name, email, title, role, emp_id),
    )
    conn.commit()
    conn.close()

    if acting_emp_id:
        log_action(acting_emp_id, "UPDATE_EMPLOYEE", details=f"Updated {emp_id}")


def delete_employee(emp_id, acting_emp_id=None):
    """
    Permanently delete an employee record.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM User WHERE EMP_ID = ?", (emp_id,))
    conn.commit()
    conn.close()

    if acting_emp_id:
        log_action(acting_emp_id, "DELETE_EMPLOYEE", details=f"Deleted {emp_id}")


def authenticate_user(emp_id, password):
    """
    Validate EMP_ID + PASSWORD and return the user row if valid.
    Returns None if no match is found.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM User
        WHERE EMP_ID = ? AND PASSWORD = ?
        """,
        (emp_id, password),
    )
    row = cur.fetchone()
    conn.close()
    return row


def reset_password(emp_id, email, new_password, acting_emp_id=None):
    """
    Reset a user’s password as long as EMP_ID + EMAIL match.
    Returns True if successful, False if user not found.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM User WHERE EMP_ID = ? AND EMAIL = ?",
        (emp_id, email),
    )
    user = cur.fetchone()
    if not user:
        conn.close()
        return False

    cur.execute(
        "UPDATE User SET PASSWORD = ? WHERE EMP_ID = ?",
        (new_password, emp_id),
    )
    conn.commit()
    conn.close()

    if acting_emp_id:
        log_action(acting_emp_id, "RESET_PASSWORD",
                   details=f"Reset password for {emp_id}")
    return True


def change_password(emp_id, old_password, new_password):
    """
    Change a user's password after verifying their old password.
    Returns True if changed, otherwise False.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Confirm the old password is correct
    cur.execute(
        "SELECT * FROM User WHERE EMP_ID = ? AND PASSWORD = ?",
        (emp_id, old_password),
    )
    user = cur.fetchone()
    if not user:
        conn.close()
        return False

    # Update to the new password
    cur.execute(
        "UPDATE User SET PASSWORD = ? WHERE EMP_ID = ?",
        (new_password, emp_id),
    )
    conn.commit()
    conn.close()
    return True


# ================================================================
# CUSTOMER MANAGEMENT
# ================================================================

def create_or_update_customer(cust_email, first_name, last_name, phone=None):
    """
    Insert a new customer or update an existing one.
    A customer is uniquely identified by email.
    """
    if not cust_email:
        return

    conn = get_connection()
    cur = conn.cursor()

    # Check for an existing customer
    cur.execute("SELECT * FROM Customers WHERE CUST_EMAIL = ?", (cust_email,))
    existing = cur.fetchone()

    if existing:
        # Update existing customer
        cur.execute(
            """
            UPDATE Customers
            SET FIRST_NAME = ?, LAST_NAME = ?, PHONE = ?
            WHERE CUST_EMAIL = ?
            """,
            (first_name, last_name, phone, cust_email),
        )
    else:
        # Create new customer
        cur.execute(
            """
            INSERT INTO Customers (CUST_EMAIL, FIRST_NAME, LAST_NAME, PHONE)
            VALUES (?, ?, ?, ?)
            """,
            (cust_email, first_name, last_name, phone),
        )

    conn.commit()
    conn.close()


def get_customers(search_term=None):
    """
    Return all customers, optionally filtered by email/name/phone.
    """
    conn = get_connection()
    cur = conn.cursor()

    if search_term:
        like = f"%{search_term}%"
        cur.execute(
            """
            SELECT *
            FROM Customers
            WHERE
                CUST_EMAIL LIKE ?
                OR FIRST_NAME LIKE ?
                OR LAST_NAME LIKE ?
                OR PHONE LIKE ?
            ORDER BY LAST_NAME, FIRST_NAME
            """,
            (like, like, like, like),
        )
    else:
        cur.execute("SELECT * FROM Customers ORDER BY LAST_NAME, FIRST_NAME")

    rows = cur.fetchall()
    conn.close()
    return rows


# ================================================================
# LOOKUP HELPERS
# ================================================================

def _ensure_lookup(table, column, value):
    """
    Insert a value into a lookup table only if it isn't already there.
    Used for things like locations, departments, categories, etc.
    """
    if not value:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT OR IGNORE INTO {table} ({column}) VALUES (?)", (value,))
    conn.commit()
    conn.close()


# ================================================================
# ASSET MANAGEMENT
# ================================================================

def create_asset(
    asset_id,
    description=None,
    brand=None,
    model=None,
    serial=None,
    purchase_date=None,
    cost=None,
    site_name=None,
    location_name=None,
    dept_name=None,
    category_name=None,
    image_path=None,
    available=True,
    acting_emp_id=None,
):
    """
    Create a new asset record.
    This includes optional metadata like location, site, category, and an image path.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO Asset (
            ASSET_ID,
            DESCRIPTION,
            BRAND,
            MODEL,
            SERIAL,
            PURCHASE_DATE,
            COST,
            SITE_NAME,
            LOCATION_NAME,
            DEPT_NAME,
            CATEGORY_NAME,
            IMAGE_PATH,
            AVAILABLE
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            asset_id, description, brand, model, serial,
            purchase_date, cost,
            site_name, location_name, dept_name, category_name,
            image_path, 1 if available else 0,
        ),
    )

    conn.commit()
    conn.close()

    # Log the creation for audit purposes
    if acting_emp_id:
        log_action(
            acting_emp_id,
            "ADD_ASSET",
            asset_id=asset_id,
            details=description or "",
        )
    return asset_id


def get_assets(search_term=None):
    """
    Return all assets, optionally filtered by ID, description, model, etc.
    """
    conn = get_connection()
    cur = conn.cursor()

    if search_term:
        like = f"%{search_term}%"
        cur.execute(
            """
            SELECT *
            FROM Asset
            WHERE
                ASSET_ID      LIKE ?
                OR DESCRIPTION LIKE ?
                OR BRAND       LIKE ?
                OR MODEL       LIKE ?
                OR SERIAL      LIKE ?
                OR SITE_NAME   LIKE ?
                OR LOCATION_NAME LIKE ?
                OR DEPT_NAME   LIKE ?
                OR CATEGORY_NAME LIKE ?
                OR FUNDING_SOURCE LIKE ?
                OR QUANTITY LIKE ?
                OR WARRANTY_INFO LIKE ?
            ORDER BY ASSET_ID
            """,
            (like, like, like, like, like, like, like, like, like),
        )
    else:
        cur.execute("SELECT * FROM Asset ORDER BY ASSET_ID")

    rows = cur.fetchall()
    conn.close()
    return rows

def get_inventory_report(search_term=None, filter_field=None,
                         start_date=None, end_date=None):
    """
    Inventory report with flexible filtering:
      - search_term: text typed by user
      - filter_field: which column to filter on (None = ANY field)
      - start_date, end_date: filter by PURCHASE_DATE
    """

    # Map dropdown labels to actual database columns
    field_map = {
        "Asset ID": "ASSET_ID",
        "Description": "DESCRIPTION",
        "Brand": "BRAND",
        "Model": "MODEL",
        "Serial": "SERIAL",
        "Purchase Date": "PURCHASE_DATE",
        "Cost": "COST",
        "Site": "SITE_NAME",
        "Location": "LOCATION_NAME",
        "Department": "DEPT_NAME",
        "Category": "CATEGORY_NAME",
        "Funding Source": "FUNDING_SOURCE",
        "Quantity": "QUANTITY",
        "Warranty Info": "WARRANTY_INFO",
    }

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            ASSET_ID,
            DESCRIPTION,
            BRAND,
            MODEL,
            SERIAL,
            SITE_NAME,
            LOCATION_NAME,
            DEPT_NAME,
            CATEGORY_NAME,
            AVAILABLE,
            PURCHASE_DATE,
            COST,
            FUNDING_SOURCE,
            QUANTITY,
            WARRANTY_INFO
        FROM Asset
        WHERE 1=1
    """

    params = []

    # ------------------------------------------------------------
    # TEXT SEARCH (search term + filter field)
    # ------------------------------------------------------------
    if search_term:
        if filter_field and filter_field in field_map:
            # Search only in the specific column
            col = field_map[filter_field]
            sql += f" AND {col} LIKE ?"
            params.append(f"%{search_term}%")
        else:
            # Search across ALL major text columns
            like = f"%{search_term}%"
            sql += """
                AND (
                    ASSET_ID       LIKE ?
                    OR DESCRIPTION LIKE ?
                    OR BRAND       LIKE ?
                    OR MODEL       LIKE ?
                    OR SERIAL      LIKE ?
                    OR SITE_NAME   LIKE ?
                    OR LOCATION_NAME LIKE ?
                    OR DEPT_NAME   LIKE ?
                    OR CATEGORY_NAME LIKE ?
                )
            """
            params.extend([like] * 9)

    # ------------------------------------------------------------
    # PURCHASE DATE FILTERS
    # ------------------------------------------------------------
    if start_date:
        sql += " AND date(PURCHASE_DATE) >= date(?)"
        params.append(start_date)

    if end_date:
        sql += " AND date(PURCHASE_DATE) <= date(?)"
        params.append(end_date)

    # ------------------------------------------------------------
    # ORDER THE RESULTS (looks nicer for reports)
    # ------------------------------------------------------------
    sql += " ORDER BY CATEGORY_NAME, SITE_NAME, LOCATION_NAME, ASSET_ID"

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows



# ================================================================
# ASSET DETAILS / UPDATE / DELETE
# ================================================================

def get_asset(asset_id):
    """
    Return a single asset row, or None if the asset doesn't exist.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            ASSET_ID,
            DESCRIPTION,
            BRAND,
            MODEL,
            SERIAL,
            PURCHASE_DATE,
            COST,
            QUANTITY,
            FUNDING_SOURCE,
            WARRANTY_INFO,
            SITE_NAME,
            LOCATION_NAME,
            DEPT_NAME,
            CATEGORY_NAME,
            IMAGE_PATH,
            AVAILABLE
        FROM Asset
        WHERE ASSET_ID = ?
        """,
        (asset_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_asset(
    asset_id,
    description=None,
    brand=None,
    model=None,
    serial=None,
    purchase_date=None,
    cost=None,
    site_name=None,
    location_name=None,
    dept_name=None,
    category_name=None,
    image_path=None,
    available=True,
    acting_emp_id=None,
):
    """
    Update an asset's details. The ASSET_ID itself cannot be changed.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE Asset
        SET
            DESCRIPTION    = ?,
            BRAND          = ?,
            MODEL          = ?,
            SERIAL         = ?,
            PURCHASE_DATE  = ?,
            COST           = ?,
            SITE_NAME      = ?,
            LOCATION_NAME  = ?,
            DEPT_NAME      = ?,
            CATEGORY_NAME  = ?,
            IMAGE_PATH     = ?,
            AVAILABLE      = ?
        WHERE ASSET_ID = ?
        """,
        (
            description, brand, model, serial, purchase_date, cost,
            site_name, location_name, dept_name, category_name,
            image_path, 1 if available else 0, asset_id
        ),
    )

    conn.commit()
    conn.close()

    if acting_emp_id:
        log_action(acting_emp_id, "UPDATE_ASSET",
                   asset_id=asset_id, details=description or "")


def delete_asset(asset_id, acting_emp_id=None):
    """
    Delete an asset entirely.
    (A real system might soft-delete or check for active checkouts.)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Sanity check: make sure the asset actually exists
    cur.execute("SELECT 1 FROM Asset WHERE ASSET_ID = ?", (asset_id,))
    exists = cur.fetchone()
    if not exists:
        conn.close()
        raise ValueError(f"Asset {asset_id} does not exist.")

    cur.execute("DELETE FROM Asset WHERE ASSET_ID = ?", (asset_id,))
    conn.commit()
    conn.close()

    if acting_emp_id:
        log_action(acting_emp_id, "DELETE_ASSET",
                   asset_id=asset_id, details=f"Deleted asset {asset_id}")


# ================================================================
# MAINTENANCE LOGGING
# ================================================================

def add_maintenance_entry(asset_id, emp_id, note):
    """
    Add a maintenance note for an asset.
    This simply logs a 'MAINTENANCE' action into AuditLog.
    """
    if not asset_id or not emp_id or not note:
        raise ValueError("asset_id, emp_id, and note are required for maintenance entry.")

    conn = get_connection()
    cur = conn.cursor()

    # Verify the asset exists
    cur.execute("SELECT 1 FROM Asset WHERE ASSET_ID = ?", (asset_id,))
    exists = cur.fetchone()
    conn.close()
    if not exists:
        raise ValueError(f"Asset {asset_id} does not exist.")

    log_action(
        emp_id,
        "MAINTENANCE",
        asset_id=asset_id,
        details=note,
    )


def get_maintenance_log(asset_id=None, start_date=None, end_date=None):
    """
    Return maintenance entries, optionally filtered by:
      - asset_id
      - start_date / end_date (YYYY-MM-DD)
    """
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            l.LOG_NO,
            l.LOG_DATE,
            l.ASSET_ID,
            a.DESCRIPTION AS ASSET_DESCRIPTION,
            l.EMP_ID,
            u.FIRST_NAME,
            u.LAST_NAME,
            l.DETAILS
        FROM AuditLog l
        LEFT JOIN Asset a ON l.ASSET_ID = a.ASSET_ID
        LEFT JOIN User  u ON l.EMP_ID   = u.EMP_ID
        WHERE l.ACTION = 'MAINTENANCE'
    """

    params = []

    # Filters
    if asset_id:
        sql += " AND l.ASSET_ID = ?"
        params.append(asset_id)

    if start_date:
        # If date only, convert to beginning of day
        s = start_date.strip()
        if len(s) == 10:
            s += "T00:00:00"
        sql += " AND l.LOG_DATE >= ?"
        params.append(s)

    if end_date:
        e = end_date.strip()
        if len(e) == 10:
            e += "T23:59:59"
        sql += " AND l.LOG_DATE <= ?"
        params.append(e)

    sql += " ORDER BY l.LOG_DATE DESC"

    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return rows


# ================================================================
# AUDIT LOG / REPORTING
# ================================================================

def get_audit_log(action=None, asset_id=None, emp_id=None, start_date=None, end_date=None):
    """
    General-purpose audit log search.
    Supports filtering by:
      - action type
      - asset_id
      - employee ID
      - start/end date
    """
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            l.LOG_NO,
            l.LOG_DATE,
            l.ACTION,
            l.ASSET_ID,
            a.DESCRIPTION AS ASSET_DESCRIPTION,
            l.EMP_ID,
            u.FIRST_NAME,
            u.LAST_NAME,
            l.DETAILS
        FROM AuditLog l
        LEFT JOIN Asset a ON l.ASSET_ID = a.ASSET_ID
        LEFT JOIN User  u ON l.EMP_ID   = u.EMP_ID
        WHERE 1 = 1
    """

    params = []

    if action:
        sql += " AND l.ACTION = ?"
        params.append(action)

    if asset_id:
        sql += " AND l.ASSET_ID = ?"
        params.append(asset_id)

    if emp_id:
        sql += " AND l.EMP_ID = ?"
        params.append(emp_id)

    if start_date:
        s = start_date.strip()
        if len(s) == 10:
            s += "T00:00:00"
        sql += " AND l.LOG_DATE >= ?"
        params.append(s)

    if end_date:
        e = end_date.strip()
        if len(e) == 10:
            e += "T23:59:59"
        sql += " AND l.LOG_DATE <= ?"
        params.append(e)

    sql += " ORDER BY l.LOG_DATE DESC"

    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return rows


# ================================================================
# CHECKOUT / CHECKIN
# ================================================================

def checkout_asset(asset_id, cust_email, checked_out_by_emp_id, due_date=None, notes=None):
    """
    Check out an asset to a customer.
    - Validates availability
    - Creates a checkout record
    - Marks asset unavailable
    - Supports optional due date and notes
    """
    if not asset_id or not cust_email:
        raise ValueError("asset_id and cust_email are required for checkout.")

    conn = get_connection()
    cur = conn.cursor()

    # Ensure asset exists + is available
    cur.execute("SELECT * FROM Asset WHERE ASSET_ID = ?", (asset_id,))
    asset = cur.fetchone()
    if not asset:
        conn.close()
        raise ValueError(f"Asset {asset_id} does not exist.")
    if not asset["AVAILABLE"]:
        conn.close()
        raise ValueError(f"Asset {asset_id} is not currently available.")

    now = datetime.now().isoformat(timespec="seconds")

    # Normalize the due date to a full ISO timestamp
    due_iso = None
    if due_date:
        due_iso = due_date.strip()
        if len(due_iso) == 10:  # YYYY-MM-DD
            due_iso += "T23:59:59"

    # Insert the checkout record
    cur.execute(
        """
        INSERT INTO Checkout (CUST_EMAIL, ASSET_ID, CHECK_OUT, CHECK_IN, DUE_DATE)
        VALUES (?, ?, ?, NULL, ?)
        """,
        (cust_email, asset_id, now, due_iso),
    )

    # Mark asset unavailable
    cur.execute(
        "UPDATE Asset SET AVAILABLE = 0 WHERE ASSET_ID = ?",
        (asset_id,),
    )

    conn.commit()
    conn.close()

    # Log checkout
    if checked_out_by_emp_id:
        details = f"Checked out to {cust_email}"
        if due_iso:
            details += f"; due {due_iso}"
        if notes:
            details += f"; notes: {notes}"

        log_action(
            checked_out_by_emp_id,
            "CHECKOUT",
            asset_id=asset_id,
            details=details,
        )


def checkin_transaction(transaction_no, acting_emp_id=None):
    """
    Check in a previously checked-out asset.
    - Closes the checkout record
    - Marks the asset available again
    """
    conn = get_connection()
    cur = conn.cursor()

    # Look up the transaction
    cur.execute("SELECT * FROM Checkout WHERE TRANSACTION_NO = ?", (transaction_no,))
    tx = cur.fetchone()
    if not tx:
        conn.close()
        raise ValueError(f"Transaction {transaction_no} not found.")

    if tx["CHECK_IN"] is not None:
        conn.close()
        raise ValueError("This transaction is already checked in.")

    asset_id = tx["ASSET_ID"]
    now = datetime.now().isoformat(timespec="seconds")

    # Update checkout record
    cur.execute(
        "UPDATE Checkout SET CHECK_IN = ? WHERE TRANSACTION_NO = ?",
        (now, transaction_no),
    )

    # Mark asset available
    cur.execute(
        "UPDATE Asset SET AVAILABLE = 1 WHERE ASSET_ID = ?",
        (asset_id,),
    )

    conn.commit()
    conn.close()

    # Log checkin
    if acting_emp_id:
        log_action(
            acting_emp_id,
            "CHECKIN",
            asset_id=asset_id,
            details=f"Checked in transaction {transaction_no}",
        )


def get_active_checkouts():
    """
    Return all ongoing checkouts (CHECK_IN is NULL),
    including joined customer + asset info.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            c.TRANSACTION_NO,
            c.ASSET_ID,
            a.DESCRIPTION AS ASSET_DESCRIPTION,
            c.CUST_EMAIL,
            cust.FIRST_NAME,
            cust.LAST_NAME,
            c.CHECK_OUT,
            c.DUE_DATE
        FROM Checkout c
        JOIN Asset a
            ON c.ASSET_ID = a.ASSET_ID
        JOIN Customers cust
            ON c.CUST_EMAIL = cust.CUST_EMAIL
        WHERE c.CHECK_IN IS NULL
        ORDER BY c.CHECK_OUT DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# ================================================================
# RESERVATIONS
# ================================================================

def create_reservation(asset_id, requested_by_emp_id, reserved_for, target_date=None):
    """
    Create a reservation for an asset.
    Reserves an asset for a person and an optional target date.
    """
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().isoformat(timespec="seconds")

    # Normalize target date
    target_iso = None
    if target_date:
        target_iso = target_date.strip()
        if len(target_iso) == 10:  # YYYY-MM-DD
            target_iso += "T00:00:00"

    cur.execute(
        """
        INSERT INTO Reservation (
            ASSET_ID,
            REQUESTED_BY,
            RESERVED_FOR,
            TARGET_DATE,
            CREATED_AT,
            STATUS
        )
        VALUES (?, ?, ?, ?, ?, 'ACTIVE')
        """,
        (asset_id, requested_by_emp_id, reserved_for, target_iso, now)
    )

    conn.commit()
    conn.close()

    # Log reservation
    log_action(
        requested_by_emp_id,
        "RESERVE_ASSET",
        asset_id=asset_id,
        details=f"Reserved for {reserved_for}, target {target_iso or 'N/A'}",
    )


def get_active_reservations_for_asset(asset_id):
    """
    Return all active reservations for a given asset.
    Sorted so that ones with no target date show last.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM Reservation
        WHERE ASSET_ID = ? AND STATUS = 'ACTIVE'
        ORDER BY 
            TARGET_DATE IS NULL, 
            TARGET_DATE, 
            CREATED_AT
        """,
        (asset_id,)
    )

    rows = cur.fetchall()
    conn.close()
    return rows
