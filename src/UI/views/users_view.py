"""
soGUI — Users (Employee Management) View

Description:
    This file defines the UsersView, which is responsible for:
      - Listing all employee records in a table
      - Adding new employees (including setting an initial password)
      - Editing existing employees (no direct password changes here)
      - Deleting employees

    All database operations (CRUD) are handled in services.py.
    This view is strictly UI + basic validation and wiring.
"""

import customtkinter as ctk
from tkinter import ttk
from services import get_employees, create_employee, update_employee, delete_employee


class UsersView(ctk.CTkFrame):
    """
    User Management screen for admins.

    This view assumes:
      - Only admins can open it (enforced in soGUIApp / app.py).
      - EMP_ID is the primary key for employees and cannot be changed
        once created.
    """

    def __init__(self, master, acting_emp_id=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.acting_emp_id = acting_emp_id
        # Tracks which employee is currently selected in the table.
        # None means we are in "add new user" mode.
        self.selected_emp_id = None

        # ---------------- Title ----------------
        title = ctk.CTkLabel(
            self,
            text="User Management (Employees)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(pady=(10, 5))

        # ---------------- Employees table ----------------
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(
            table_frame,
            columns=("EMP_ID", "FIRST_NAME", "LAST_NAME", "EMAIL", "TITLE", "ROLE"),
            show="headings",
        )

        for col, text, width in [
            ("EMP_ID", "Emp ID", 80),
            ("FIRST_NAME", "First Name", 120),
            ("LAST_NAME", "Last Name", 120),
            ("EMAIL", "Email", 200),
            ("TITLE", "Title", 120),
            ("ROLE", "Role", 80),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)

        self.tree.pack(expand=True, fill="both")

        # When a row is selected, fill the form and switch to edit mode
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # ---------------- Add / Edit form ----------------
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=10, pady=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

        # Form state variables
        self.emp_id_var = ctk.StringVar()
        self.first_name_var = ctk.StringVar()
        self.last_name_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.title_var = ctk.StringVar()
        self.role_var = ctk.StringVar(value="standard")
        self.password_var = ctk.StringVar()

        # Row 0: Emp ID + Role
        lbl_emp = ctk.CTkLabel(form_frame, text="Emp ID:")
        lbl_emp.grid(row=0, column=0, sticky="w", pady=5)
        self.ent_emp = ctk.CTkEntry(form_frame, textvariable=self.emp_id_var)
        self.ent_emp.grid(row=0, column=1, sticky="ew", pady=5, padx=(0, 10))

        lbl_role = ctk.CTkLabel(form_frame, text="Role:")
        lbl_role.grid(row=0, column=2, sticky="w", pady=5)
        self.opt_role = ctk.CTkOptionMenu(
            form_frame,
            variable=self.role_var,
            values=["admin", "standard"],
        )
        self.opt_role.grid(row=0, column=3, sticky="ew", pady=5)

        # Row 1: First / Last
        lbl_first = ctk.CTkLabel(form_frame, text="First Name:")
        lbl_first.grid(row=1, column=0, sticky="w", pady=5)
        self.ent_first = ctk.CTkEntry(form_frame, textvariable=self.first_name_var)
        self.ent_first.grid(row=1, column=1, sticky="ew", pady=5, padx=(0, 10))

        lbl_last = ctk.CTkLabel(form_frame, text="Last Name:")
        lbl_last.grid(row=1, column=2, sticky="w", pady=5)
        self.ent_last = ctk.CTkEntry(form_frame, textvariable=self.last_name_var)
        self.ent_last.grid(row=1, column=3, sticky="ew", pady=5)

        # Row 2: Email / Title
        lbl_email = ctk.CTkLabel(form_frame, text="Email:")
        lbl_email.grid(row=2, column=0, sticky="w", pady=5)
        self.ent_email = ctk.CTkEntry(form_frame, textvariable=self.email_var)
        self.ent_email.grid(row=2, column=1, sticky="ew", pady=5, padx=(0, 10))

        lbl_title = ctk.CTkLabel(form_frame, text="Title:")
        lbl_title.grid(row=2, column=2, sticky="w", pady=5)
        self.ent_title = ctk.CTkEntry(form_frame, textvariable=self.title_var)
        self.ent_title.grid(row=2, column=3, sticky="ew", pady=5)

        # Row 3: Password (for new users only) + buttons
        lbl_pw = ctk.CTkLabel(form_frame, text="Password (new users):")
        lbl_pw.grid(row=3, column=0, sticky="w", pady=5)
        self.ent_pw = ctk.CTkEntry(form_frame, textvariable=self.password_var, show="*")
        self.ent_pw.grid(row=3, column=1, sticky="ew", pady=5, padx=(0, 10))

        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.grid(row=3, column=3, sticky="e", pady=5)

        # Delete (only enabled when editing an existing user)
        self.btn_delete = ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=self.delete_selected,
            state="disabled",
            fg_color="#b91c1c",
            hover_color="#ef4444",
        )
        self.btn_delete.pack(side="left")

        # Update (only enabled when editing an existing user)
        self.btn_update = ctk.CTkButton(
            btn_frame,
            text="Update",
            command=self.update_selected,
            state="disabled",
        )
        self.btn_update.pack(side="left", padx=(0, 5))

        # Add new user (disabled when in edit mode)
        self.btn_add = ctk.CTkButton(
            btn_frame,
            text="Add User",
            command=self.add_employee,
        )
        self.btn_add.pack(side="left", padx=(0, 5))

        # Clear selection button below form
        clear_btn = ctk.CTkButton(
            self,
            text="Clear Selection / New Entry",
            command=self.clear_selection,
        )
        clear_btn.pack(pady=(0, 10))

        # Initial population of the table
        self.refresh_table()

    # ============================================================
    # Table handling
    # ============================================================

    def refresh_table(self):
        """
        Reload the employee table from the database.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        for emp in get_employees():
            self.tree.insert(
                "",
                "end",
                values=(
                    emp["EMP_ID"],
                    emp["FIRST_NAME"],
                    emp["LAST_NAME"],
                    emp["EMAIL"],
                    emp["TITLE"],
                    emp["ROLE"],
                ),
            )

    def on_tree_select(self, event):
        """
        When a user is selected in the table:
          - Fill the form fields with that user's info
          - Put the form into 'edit' mode
        """
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        # values order: EMP_ID, FIRST_NAME, LAST_NAME, EMAIL, TITLE, ROLE
        emp_id, first, last, email, title, role = values

        # Fill form fields
        self.selected_emp_id = emp_id
        self.emp_id_var.set(emp_id)
        self.first_name_var.set(first)
        self.last_name_var.set(last)
        self.email_var.set(email)
        self.title_var.set(title)
        self.role_var.set(role)
        # For security reasons we never load or display a password
        self.password_var.set("")

        # Switch to "edit mode"
        self.ent_emp.configure(state="disabled")  # cannot change EMP_ID
        self.btn_add.configure(state="disabled")
        self.btn_update.configure(state="normal")
        self.btn_delete.configure(state="normal")

    def clear_selection(self):
        """
        Return to 'add new user' mode and clear the form.
        """
        self.selected_emp_id = None

        self.emp_id_var.set("")
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.title_var.set("")
        self.role_var.set("standard")
        self.password_var.set("")

        self.ent_emp.configure(state="normal")
        self.btn_add.configure(state="normal")
        self.btn_update.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

        # Also clear tree selection visually
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    # ============================================================
    # Actions
    # ============================================================

    def add_employee(self):
        """
        Create a brand new employee record.

        Required for new users:
          - Emp ID
          - First name
          - Last name
          - Password
        """
        # If we're in edit mode, don't allow adding (user must clear first)
        if self.selected_emp_id is not None:
            return

        emp_id = self.emp_id_var.get().strip()
        first = self.first_name_var.get().strip()
        last = self.last_name_var.get().strip()
        email = self.email_var.get().strip() or None
        title = self.title_var.get().strip() or None
        role = self.role_var.get()
        password = self.password_var.get().strip()

        if not emp_id or not first or not last or not password:
            # In a future enhancement, this could be a status label instead of print.
            print("Emp ID, first name, last name, and password are required for new users.")
            return

        try:
            create_employee(
                emp_id=emp_id,
                first_name=first,
                last_name=last,
                email=email,
                title=title,
                role=role,
                password=password,
                acting_emp_id=self.acting_emp_id,
            )
        except Exception as e:
            print("Error creating employee:", e)
            return

        self.clear_selection()
        self.refresh_table()

    def update_selected(self):
        """
        Update the currently selected employee's info (no password change here).
        """
        if not self.selected_emp_id:
            return

        emp_id = self.selected_emp_id
        first = self.first_name_var.get().strip()
        last = self.last_name_var.get().strip()
        email = self.email_var.get().strip() or None
        title = self.title_var.get().strip() or None
        role = self.role_var.get()

        if not first or not last:
            print("First and last name are required.")
            return

        try:
            update_employee(
                emp_id=emp_id,
                first_name=first,
                last_name=last,
                email=email,
                title=title,
                role=role,
                acting_emp_id=self.acting_emp_id,
            )
        except Exception as e:
            print("Error updating employee:", e)
            return

        self.clear_selection()
        self.refresh_table()

    def delete_selected(self):
        """
        Delete the currently selected employee.

        Note:
            For a production system you would almost certainly add:
              - A confirmation dialog
              - Some kind of 'inactive' flag instead of hard delete
        """
        if not self.selected_emp_id:
            return

        emp_id = self.selected_emp_id

        try:
            delete_employee(emp_id, acting_emp_id=self.acting_emp_id)
        except Exception as e:
            print("Error deleting employee:", e)
            return

        self.clear_selection()
        self.refresh_table()


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
    root.title("UsersView debug")
    root.geometry("1000x700")

    view = UsersView(root, acting_emp_id="admin")
    view.pack(expand=True, fill="both")

    root.mainloop()