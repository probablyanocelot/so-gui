if __name__ == "__main__":
    import os
    import sys

    # Make src/ importable when running this file directly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

    import customtkinter as ctk
    from db import init_db
    from services import seed_default_admin

    # Optional: initialize DB state for view testing
    init_db()
    seed_default_admin()

    root = ctk.CTk()
    root.title("InventoryView debug")
    root.geometry("1000x700")

    view = InventoryView(root, acting_emp_id="admin")
    view.pack(expand=True, fill="both")

    root.mainloop()