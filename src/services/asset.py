from database.setup  import get_connection

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
