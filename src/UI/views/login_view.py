# TODO: modularize - (if we need the reset dialog elsewhere)
"""
soGUI — Login View

Description:
    This file defines the LoginView, which is responsible for:
      - Displaying the main login form (Employee ID + password)
      - Enforcing a simple max login attempt limit
      - Calling into the service layer to authenticate users
      - Providing a "Forgot Password" dialog that lets users
        reset their password using EMP_ID + school email.

    The view does not directly touch the database. It delegates all
    auth-related work to functions in services.py.
"""

import customtkinter as ctk
from services import authenticate_user, reset_password


class LoginView(ctk.CTkFrame):
    """
    Main login screen for soGUI.

    Args:
        master: Parent widget.
        on_login_success: callback function that receives the
            authenticated user row (sqlite3.Row) when login works.
    """

    def __init__(self, master, on_login_success, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_login_success = on_login_success

        # Simple lockout rule: after 5 failed attempts, login is disabled
        self.max_attempts = 5
        self.failed_attempts = 0

        # Form state
        self.emp_id_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        # -------- Title --------
        title = ctk.CTkLabel(
            self,
            text="soGUI Login",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(40, 10))

        # -------- Login form --------
        form = ctk.CTkFrame(self)
        form.pack(pady=10, padx=20)
        form.grid_columnconfigure(1, weight=1)

        # Employee ID
        lbl_user = ctk.CTkLabel(form, text="Employee ID:")
        lbl_user.grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        ent_user = ctk.CTkEntry(form, textvariable=self.emp_id_var)
        ent_user.grid(row=0, column=1, sticky="ew", pady=5)

        # Password
        lbl_pass = ctk.CTkLabel(form, text="Password:")
        lbl_pass.grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        ent_pass = ctk.CTkEntry(form, textvariable=self.password_var, show="*")
        ent_pass.grid(row=1, column=1, sticky="ew", pady=5)

        # Status label (for error/success messages)
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=(5, 0))

        # -------- Buttons row --------
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        # Main login button
        self.login_btn = ctk.CTkButton(
            btn_frame,
            text="Log In",
            command=self.handle_login,
        )
        self.login_btn.pack(side="left", padx=(0, 10))

        # Forgot password button
        reset_btn = ctk.CTkButton(
            btn_frame,
            text="Forgot Password",
            fg_color="gray",
            command=self.open_reset_window,
        )
        reset_btn.pack(side="left")

    # ============================================================
    # Login logic
    # ============================================================

    def handle_login(self):
        """
        Handle the login button click.

        - Reads EMP_ID + password
        - Calls authenticate_user() from services
        - Tracks failed attempts and disables login after max_attempts
        """
        # If we've already locked the login, do nothing
        if self.failed_attempts >= self.max_attempts:
            return

        emp_id = self.emp_id_var.get().strip()
        password = self.password_var.get().strip()

        user = authenticate_user(emp_id, password)
        if user:
            # Successful login
            self.status_label.configure(text="Login successful.", text_color="green")
            self.on_login_success(user)
        else:
            # Increment failure count
            self.failed_attempts += 1
            remaining = self.max_attempts - self.failed_attempts

            if remaining <= 0:
                # Lock out further attempts
                self.status_label.configure(
                    text="Too many failed attempts. Login disabled.",
                    text_color="red",
                )
                self.login_btn.configure(state="disabled")
            else:
                self.status_label.configure(
                    text=f"Invalid credentials. {remaining} attempt(s) remaining.",
                    text_color="red",
                )



    # ============================================================
    # Password reset dialog
    # ============================================================

    def open_reset_window(self):
        """
        Open a small dialog to reset a password using EMP_ID + school email.

        For this class project, this directly calls reset_password()
        from services.py and does not send any email.
        """
        win = ctk.CTkToplevel(self)
        win.title("Reset Password")
        win.geometry("400x260")
        win.grab_set()  # modal window

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

        emp_id_var = ctk.StringVar()
        email_var = ctk.StringVar()
        new_pass_var = ctk.StringVar()

        # Employee ID
        lbl_u = ctk.CTkLabel(frame, text="Employee ID:")
        lbl_u.grid(row=0, column=0, sticky="w", pady=5)
        ent_u = ctk.CTkEntry(frame, textvariable=emp_id_var)
        ent_u.grid(row=0, column=1, pady=5, sticky="ew")

        # School email
        lbl_e = ctk.CTkLabel(frame, text="School Email:")
        lbl_e.grid(row=1, column=0, sticky="w", pady=5)
        ent_e = ctk.CTkEntry(frame, textvariable=email_var)
        ent_e.grid(row=1, column=1, pady=5, sticky="ew")

        # New password
        lbl_p = ctk.CTkLabel(frame, text="New Password:")
        lbl_p.grid(row=2, column=0, sticky="w", pady=5)
        ent_p = ctk.CTkEntry(frame, textvariable=new_pass_var, show="*")
        ent_p.grid(row=2, column=1, pady=5, sticky="ew")

        status_lbl = ctk.CTkLabel(frame, text="")
        status_lbl.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        def do_reset():
            """
            Validate the reset form and attempt to reset the password.
            """
            emp_id = emp_id_var.get().strip()
            email = email_var.get().strip()
            new_pw = new_pass_var.get().strip()

            if not emp_id or not email or not new_pw:
                status_lbl.configure(text="All fields are required.", text_color="red")
                return

            ok = reset_password(emp_id, email, new_pw)
            if ok:
                status_lbl.configure(text="Password reset successfully.", text_color="green")
            else:
                status_lbl.configure(
                    text="No matching active user for that email.",
                    text_color="red",
                )

        # Bottom row of buttons for the reset dialog
        btn_row = ctk.CTkFrame(win)
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(btn_row, text="Reset", command=do_reset)
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Close",
            fg_color="gray",
            command=win.destroy,
        )
        cancel_btn.pack(side="right")


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
    root.title("LoginView debug")
    root.geometry("1000x700")

    view = LoginView(root,
            on_login_success=lambda: print("Login successful!"))
    view.pack(expand=True, fill="both")

    root.mainloop()