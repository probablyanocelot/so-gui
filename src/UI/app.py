"""
soGUI — Main UI Application

Description:
    This file defines the main soGUIApp window using CustomTkinter.
    It handles:
      - Overall layout (sidebar + main content area)
      - Switching between different views (Inventory, Users, Checkout, Reports)
      - Tracking the currently logged-in user
      - Basic session actions like login, logout, and change password

    The heavy lifting for each screen lives in the separate view
    classes (InventoryView, UsersView, CheckoutView, ReportsView, LoginView).
"""

import customtkinter as ctk

from ..old.inventory_view import InventoryView
from ..old.users_view import UsersView
from ..old.checkout_view import CheckoutView
from ..old.reports_view import ReportsView
from ..old.login_view import LoginView


class soGUIApp(ctk.CTk):
    """
    Main application window for soGUI.

    This class sets up the top-level window, creates the sidebar
    navigation, and manages which view is currently active in
    the main content area.
    """

    def __init__(self):
        super().__init__()

        # Will hold the logged-in user row (from User table) or None
        self.current_user = None

        # Basic window setup
        self.title("soGUI - Slightly Optimized Management System")
        self.geometry("1000x600")

        # Theme settings for the app
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Layout: sidebar (col 0) + main content (col 1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- Sidebar ----------------
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(6, weight=1)  # push lower buttons down

        # Simple logo / title label
        logo = ctk.CTkLabel(
            self.sidebar,
            text="soGUI",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Shows logged-in user or "Not logged in"
        self.user_label = ctk.CTkLabel(self.sidebar, text="Not logged in")
        self.user_label.grid(row=1, column=0, padx=20, pady=(0, 10))

        # Navigation buttons (disabled until login succeeds)
        self.btn_inventory = ctk.CTkButton(
            self.sidebar,
            text="Inventory",
            command=self.show_inventory_view,
            state="disabled",
        )
        self.btn_inventory.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_users = ctk.CTkButton(
            self.sidebar,
            text="Users",
            command=self.show_users_view,
            state="disabled",
        )
        self.btn_users.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_checkout = ctk.CTkButton(
            self.sidebar,
            text="Check In / Out",
            command=self.show_checkout_view,
            state="disabled",
        )
        self.btn_checkout.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_reports = ctk.CTkButton(
            self.sidebar,
            text="Reports / Logs",
            command=self.show_reports_view,
            state="disabled",
        )
        self.btn_reports.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # Change Password button (enabled after login)
        self.btn_change_password = ctk.CTkButton(
            self.sidebar,
            text="Change Password",
            state="disabled",
            command=self.open_change_password_window,
        )
        self.btn_change_password.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        # Logout button
        self.btn_logout = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="red",
            state="disabled",
            command=self.logout,
        )
        self.btn_logout.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="ew")

        # ---------------- Main area ----------------
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nswe")

        # Will hold the currently active view widget (LoginView, InventoryView, etc.)
        self.current_view = None

        # Start the app on the login screen
        self.show_login_view()

    # ============================================================
    # Helper methods
    # ============================================================

    def clear_main(self):
        """
        Destroy the currently active view in the main area, if any.
        """
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = None

    # ============================================================
    # Login / Session handling
    # ============================================================

    def show_login_view(self):
        """
        Show the login view in the main content area.
        """
        self.clear_main()
        self.current_view = LoginView(
            self.main_frame,
            on_login_success=self.on_login_success,
        )
        self.current_view.pack(expand=True, fill="both")

    def on_login_success(self, user_row):
        """
        Callback used by LoginView after a successful login.

        Args:
            user_row: sqlite3.Row containing the logged-in user's data.
        """
        self.current_user = user_row
        emp_id = user_row["EMP_ID"]
        role = user_row["ROLE"]

        # Update sidebar label with basic user info
        self.user_label.configure(text=f"{emp_id} ({role})")

        # Enable navigation after login
        self.btn_inventory.configure(state="normal")
        # Only admins can manage users
        self.btn_users.configure(state="normal" if role == "admin" else "disabled")
        self.btn_checkout.configure(state="normal")
        self.btn_reports.configure(state="normal")
        self.btn_change_password.configure(state="normal")
        self.btn_logout.configure(state="normal")

        # Default landing page after login
        self.show_inventory_view()

    # ============================================================
    # View switchers
    # ============================================================

    def show_inventory_view(self):
        """
        Switch to the Inventory screen (if a user is logged in).
        """
        if not self.current_user:
            return
        self.clear_main()
        self.current_view = InventoryView(
            self.main_frame,
            acting_emp_id=self.current_user["EMP_ID"],
        )
        self.current_view.pack(expand=True, fill="both")

    def show_users_view(self):
        """
        Switch to the Users screen.

        Only admins should be able to access this screen.
        """
        if not self.current_user:
            return
        if self.current_user["ROLE"] != "admin":
            return

        self.clear_main()
        self.current_view = UsersView(
            self.main_frame,
            acting_emp_id=self.current_user["EMP_ID"],
        )
        self.current_view.pack(expand=True, fill="both")

    def show_checkout_view(self):
        """
        Switch to the Check In / Out screen.
        """
        if not self.current_user:
            return
        self.clear_main()
        self.current_view = CheckoutView(
            self.main_frame,
            acting_emp_id=self.current_user["EMP_ID"],
        )
        self.current_view.pack(expand=True, fill="both")

    def show_reports_view(self):
        """
        Switch to the Reports / Logs screen.
        """
        if not self.current_user:
            return
        self.clear_main()
        self.current_view = ReportsView(
            self.main_frame,
            acting_emp_id=self.current_user["EMP_ID"],
        )
        self.current_view.pack(expand=True, fill="both")

    def logout(self):
        """
        Clear the current session and return to the login screen.
        """
        self.current_user = None
        self.user_label.configure(text="Not logged in")

        # Disable all navigation and session-related buttons
        self.btn_inventory.configure(state="disabled")
        self.btn_users.configure(state="disabled")
        self.btn_checkout.configure(state="disabled")
        self.btn_reports.configure(state="disabled")
        self.btn_change_password.configure(state="disabled")
        self.btn_logout.configure(state="disabled")

        # Reset current view and show login again
        self.clear_main()
        self.show_login_view()

    # ============================================================
    # Change Password dialog
    # ============================================================

    def open_change_password_window(self):
        """
        Open a small pop-up window that lets the current user
        change their password.
        """
        if not self.current_user:
            return

        # Local import to avoid circular imports at module load time
        from services import change_password

        emp_id = self.current_user["EMP_ID"]

        # Basic toplevel dialog
        win = ctk.CTkToplevel(self)
        win.title("Change Password")
        win.geometry("400x260")
        win.grab_set()  # make this window modal

        # Main frame inside the dialog
        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

        # Tkinter StringVar objects for collecting input
        old_pw_var = ctk.StringVar()
        new_pw_var = ctk.StringVar()
        confirm_pw_var = ctk.StringVar()

        # --- Current password ---
        lbl_old = ctk.CTkLabel(frame, text="Current Password:")
        lbl_old.grid(row=0, column=0, sticky="w", pady=5)
        ent_old = ctk.CTkEntry(frame, textvariable=old_pw_var, show="*")
        ent_old.grid(row=0, column=1, sticky="ew", pady=5)

        # --- New password ---
        lbl_new = ctk.CTkLabel(frame, text="New Password:")
        lbl_new.grid(row=1, column=0, sticky="w", pady=5)
        ent_new = ctk.CTkEntry(frame, textvariable=new_pw_var, show="*")
        ent_new.grid(row=1, column=1, sticky="ew", pady=5)

        # --- Confirm new password ---
        lbl_conf = ctk.CTkLabel(frame, text="Confirm New Password:")
        lbl_conf.grid(row=2, column=0, sticky="w", pady=5)
        ent_conf = ctk.CTkEntry(frame, textvariable=confirm_pw_var, show="*")
        ent_conf.grid(row=2, column=1, sticky="ew", pady=5)

        # Status label (for errors/success messages)
        status_lbl = ctk.CTkLabel(frame, text="")
        status_lbl.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        def do_change():
            """
            Validate the password fields and call the service function
            to actually update the password.
            """
            old_pw = old_pw_var.get().strip()
            new_pw = new_pw_var.get().strip()
            conf_pw = confirm_pw_var.get().strip()

            # Basic validation of input
            if not old_pw or not new_pw or not conf_pw:
                status_lbl.configure(text="All fields are required.", text_color="red")
                return

            if new_pw != conf_pw:
                status_lbl.configure(text="New passwords do not match.", text_color="red")
                return

            # Call service layer to update password
            ok = change_password(emp_id, old_pw, new_pw)
            if ok:
                status_lbl.configure(text="Password changed successfully.", text_color="green")
            else:
                status_lbl.configure(text="Current password is incorrect.", text_color="red")

        # Button row at the bottom of the dialog
        btn_row = ctk.CTkFrame(win)
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(btn_row, text="Change", command=do_change)
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Close",
            fg_color="gray",
            command=win.destroy,
        )
        cancel_btn.pack(side="right")
