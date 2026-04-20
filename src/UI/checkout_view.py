"""
soGUI — Checkout / Check-in View

Description:
    This file defines the CheckoutView, which handles:
      - Viewing available assets and checking them out to customers
      - Creating or updating basic customer info during checkout
      - Listing all active checkouts
      - Checking assets back in
      - Creating reservations for assets that are currently checked out

    The actual database work is handled by functions in services.py.
    This view is responsible for UI layout and calling those helpers.
"""

import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

from services import (
    get_assets,
    create_or_update_customer,
    checkout_asset,
    get_active_checkouts,
    checkin_transaction,
    create_reservation,
    get_active_reservations_for_asset,
)


class CheckoutView(ctk.CTkFrame):
    """
    Main frame for the "Check Out / Check In" tab.

    This control creates two tabs:
      - "Check Out": Select an available asset, enter customer info, and check out.
      - "Active Checkouts / Check In": See current checkouts, check assets back in,
        and optionally create reservations.
    """

    def __init__(self, master, acting_emp_id=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.acting_emp_id = acting_emp_id  # who is performing the actions

        # Used when creating a reservation from an active checkout
        self.selected_active_asset_id = None

        # Header label for the view
        title = ctk.CTkLabel(
            self,
            text="Check Out / Check In",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(pady=(10, 5))

        # Tab container: "Check Out" + "Active Checkouts / Check In"
        tabs = ctk.CTkTabview(self)
        tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_checkout = tabs.add("Check Out")
        self.tab_active = tabs.add("Active Checkouts / Check In")

        # Build each tab layout
        self._build_checkout_tab()
        self._build_active_tab()

    # ============================================================
    # Check Out tab
    # ============================================================

    def _build_checkout_tab(self):
        """
        Build the layout for the "Check Out" tab:
          - Left side: list of available assets
          - Right side: customer + checkout form
        """
        # Outer frame for this tab
        top = ctk.CTkFrame(self.tab_checkout)
        top.pack(expand=True, fill="both", padx=10, pady=(10, 5))

        # Left side: table of available assets
        left = ctk.CTkFrame(top)
        left.pack(side="left", expand=True, fill="both", padx=(0, 5))

        # Right side: form to enter checkout info
        right = ctk.CTkFrame(top)
        right.pack(side="left", fill="y", padx=(5, 0))

        # ------------ Available assets list ------------
        lbl_assets = ctk.CTkLabel(
            left,
            text="Available Assets",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_assets.pack(pady=(0, 5))

        # Treeview showing available assets only
        assets_table_frame = ctk.CTkFrame(left)
        assets_table_frame.pack(expand=True, fill="both")

        self.assets_tree = ttk.Treeview(
            assets_table_frame,
            columns=("ASSET_ID", "DESCRIPTION", "BRAND", "MODEL"),
            show="headings",
            height=12,
        )
        for col, text, width in [
            ("ASSET_ID", "Asset ID", 90),
            ("DESCRIPTION", "Description", 200),
            ("BRAND", "Brand", 100),
            ("MODEL", "Model", 120),
        ]:
            self.assets_tree.heading(col, text=text)
            self.assets_tree.column(col, width=width)

        vsb = ttk.Scrollbar(assets_table_frame, orient="vertical", command=self.assets_tree.yview)
        hsb = ttk.Scrollbar(assets_table_frame, orient="horizontal", command=self.assets_tree.xview)
        self.assets_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.assets_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        assets_table_frame.rowconfigure(0, weight=1)
        assets_table_frame.columnconfigure(0, weight=1)

        # When a row is selected, we update the Asset ID in the form
        self.assets_tree.bind("<<TreeviewSelect>>", self.on_asset_select)

        # ------------ Customer + checkout form ------------
        form = ctk.CTkFrame(right)
        form.pack(fill="y", padx=5, pady=5)
        form.grid_columnconfigure(1, weight=1)

        lbl_form_title = ctk.CTkLabel(
            form,
            text="Check Out Asset",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_form_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Tk variables for fields
        self.asset_id_var = ctk.StringVar()
        self.cust_email_var = ctk.StringVar()
        self.cust_first_var = ctk.StringVar()
        self.cust_last_var = ctk.StringVar()
        self.cust_phone_var = ctk.StringVar()
        self.due_date_var = ctk.StringVar()
        self.notes_var = ctk.StringVar()

        # Asset ID (auto-filled when you click in the table or can be typed manually)
        lbl_asset = ctk.CTkLabel(form, text="Asset ID:")
        lbl_asset.grid(row=1, column=0, sticky="w", pady=3)
        ent_asset = ctk.CTkEntry(form, textvariable=self.asset_id_var)
        ent_asset.grid(row=1, column=1, sticky="ew", pady=3)

        # Customer email (primary key for Customers table)
        lbl_email = ctk.CTkLabel(form, text="Customer Email:")
        lbl_email.grid(row=2, column=0, sticky="w", pady=3)
        ent_email = ctk.CTkEntry(form, textvariable=self.cust_email_var)
        ent_email.grid(row=2, column=1, sticky="ew", pady=3)

        # First name
        lbl_fn = ctk.CTkLabel(form, text="First Name:")
        lbl_fn.grid(row=3, column=0, sticky="w", pady=3)
        ent_fn = ctk.CTkEntry(form, textvariable=self.cust_first_var)
        ent_fn.grid(row=3, column=1, sticky="ew", pady=3)

        # Last name
        lbl_ln = ctk.CTkLabel(form, text="Last Name:")
        lbl_ln.grid(row=4, column=0, sticky="w", pady=3)
        ent_ln = ctk.CTkEntry(form, textvariable=self.cust_last_var)
        ent_ln.grid(row=4, column=1, sticky="ew", pady=3)

        # Phone
        lbl_phone = ctk.CTkLabel(form, text="Phone:")
        lbl_phone.grid(row=5, column=0, sticky="w", pady=3)
        ent_phone = ctk.CTkEntry(form, textvariable=self.cust_phone_var)
        ent_phone.grid(row=5, column=1, sticky="ew", pady=3)

        # Due date (optional, stored as ISO string in DB)
        lbl_due = ctk.CTkLabel(form, text="Due back (YYYY-MM-DD):")
        lbl_due.grid(row=6, column=0, sticky="w", pady=3)
        ent_due = ctk.CTkEntry(form, textvariable=self.due_date_var)
        ent_due.grid(row=6, column=1, sticky="ew", pady=3)

        # Simple notes field (stored on the audit log side, not the asset)
        lbl_notes = ctk.CTkLabel(form, text="Notes:")
        lbl_notes.grid(row=7, column=0, sticky="w", pady=3)
        ent_notes = ctk.CTkEntry(form, textvariable=self.notes_var)
        ent_notes.grid(row=7, column=1, sticky="ew", pady=3)

        # Status label for errors/success messages on checkout
        self.checkout_status = ctk.CTkLabel(form, text="")
        self.checkout_status.grid(row=8, column=0, columnspan=2, pady=(5, 0))

        # Main button to perform the checkout
        btn_checkout = ctk.CTkButton(
            form,
            text="Check Out",
            command=self.do_checkout,
        )
        btn_checkout.grid(row=9, column=1, sticky="e", pady=(10, 0))

        # Initial load of available assets
        self.refresh_available_assets()

    def refresh_available_assets(self):
        """
        Reload the "Available Assets" table with assets that
        are currently AVAILABLE = 1.
        """
        # Clear existing rows
        for row in self.assets_tree.get_children():
            self.assets_tree.delete(row)

        # get_assets() returns all assets; we filter by AVAILABLE here
        for asset in get_assets():
            if asset["AVAILABLE"]:
                self.assets_tree.insert(
                    "",
                    "end",
                    values=(
                        asset["ASSET_ID"],
                        asset["DESCRIPTION"],
                        asset["BRAND"],
                        asset["MODEL"],
                    ),
                )

    def on_asset_select(self, event):
        """
        When an asset is selected in the left-hand table,
        copy its ASSET_ID into the checkout form.
        """
        selected = self.assets_tree.selection()
        if not selected:
            return
        item_id = selected[0]
        values = self.assets_tree.item(item_id, "values")
        asset_id = values[0]
        self.asset_id_var.set(asset_id)

    def do_checkout(self):
        """
        Validate the form and perform a checkout:
          - Ensures required fields are present
          - Creates/updates the customer record
          - Calls the services.checkout_asset() function
          - Clears the form and updates tables on success
        """
        asset_id = self.asset_id_var.get().strip()
        cust_email = self.cust_email_var.get().strip()
        first = self.cust_first_var.get().strip()
        last = self.cust_last_var.get().strip()
        phone = self.cust_phone_var.get().strip() or None
        due_date = self.due_date_var.get().strip() or None
        notes = self.notes_var.get().strip() or None

        # Basic required fields check
        if not asset_id or not cust_email or not first or not last:
            self.checkout_status.configure(
                text="Asset ID, email, first, and last name are required.",
                text_color="red",
            )
            return

        try:
            # Make sure the customer exists (or update their info)
            create_or_update_customer(cust_email, first, last, phone)

            # Perform the actual checkout in the service layer
            checkout_asset(
                asset_id=asset_id,
                cust_email=cust_email,
                checked_out_by_emp_id=self.acting_emp_id,
                due_date=due_date,
                notes=notes,
            )
        except Exception as e:
            # Any error from the service layer shows up here
            self.checkout_status.configure(text=str(e), text_color="red")
            return

        # Success message
        self.checkout_status.configure(text="Checked out successfully.", text_color="green")

        # Clear out the form fields for the next checkout
        self.asset_id_var.set("")
        self.cust_email_var.set("")
        self.cust_first_var.set("")
        self.cust_last_var.set("")
        self.cust_phone_var.set("")
        self.due_date_var.set("")
        self.notes_var.set("")

        # Refresh tables so availability + active checkouts stay synced
        self.refresh_available_assets()
        self.refresh_active_checkouts()

    # ============================================================
    # Active Checkouts tab
    # ============================================================

    def _build_active_tab(self):
        """
        Build the layout for the "Active Checkouts / Check In" tab:
          - Table of all currently active checkouts
          - Buttons to check in and to create a reservation
        """
        frame = ctk.CTkFrame(self.tab_active)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Top area: label/title
        top = ctk.CTkFrame(frame)
        top.pack(fill="x", pady=(0, 5))

        lbl = ctk.CTkLabel(
            top,
            text="Assets Currently Checked Out",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl.pack(side="left")

        # Middle area: Treeview listing all active checkouts
        table_frame = ctk.CTkFrame(frame)
        table_frame.pack(expand=True, fill="both")

        self.active_tree = ttk.Treeview(
            table_frame,
            columns=(
                "TRANSACTION_NO",
                "ASSET_ID",
                "ASSET_DESCRIPTION",
                "CUST_EMAIL",
                "CUSTOMER_NAME",
                "CHECK_OUT",
                "DUE_DATE",
            ),
            show="headings",
        )

        for col, text, width in [
            ("TRANSACTION_NO", "Trans #", 80),
            ("ASSET_ID", "Asset ID", 90),
            ("ASSET_DESCRIPTION", "Description", 200),
            ("CUST_EMAIL", "Customer Email", 160),
            ("CUSTOMER_NAME", "Customer Name", 160),
            ("CHECK_OUT", "Checked Out At", 150),
            ("DUE_DATE", "Due Back", 150),
        ]:
            self.active_tree.heading(col, text=text)
            self.active_tree.column(col, width=width)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.active_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.active_tree.xview)
        self.active_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.active_tree.grid(row=0, column=0, sticky="nsew", pady=(5, 5))
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # When a row is selected, we store that asset_id for potential reservation
        self.active_tree.bind("<<TreeviewSelect>>", self.on_active_select)

        # Bottom area: status + buttons
        bottom = ctk.CTkFrame(frame)
        bottom.pack(fill="x", pady=(0, 5))

        self.checkin_status = ctk.CTkLabel(bottom, text="")
        self.checkin_status.pack(side="left", padx=5)

        # Reserve button (enabled when a checkout is selected)
        self.btn_reserve = ctk.CTkButton(
            bottom,
            text="Reserve Asset",
            state="disabled",
            command=self.open_reserve_window,
        )
        self.btn_reserve.pack(side="right", padx=5)

        # Check-in button
        btn_checkin = ctk.CTkButton(
            bottom,
            text="Check In Selected",
            command=self.do_checkin_selected,
        )
        btn_checkin.pack(side="right", padx=5)

        # Initial load of active checkouts
        self.refresh_active_checkouts()

    def on_active_select(self, event=None):
        """
        Handle selection in the 'Assets Currently Checked Out' table.

        Stores the selected asset ID and enables the Reserve button.
        """
        selected = self.active_tree.selection()
        if not selected:
            self.selected_active_asset_id = None
            if hasattr(self, "btn_reserve"):
                self.btn_reserve.configure(state="disabled")
            
            # Clear status when nothing is selected
            self.checkin_status.configure(text="", text_color="gray")
            return

        item_id = selected[0]
        values = self.active_tree.item(item_id, "values")
        # Column order:
        #   TRANSACTION_NO, ASSET_ID, ASSET_DESCRIPTION,
        #   CUST_EMAIL, CUSTOMER_NAME, CHECK_OUT, DUE_DATE
        self.selected_active_asset_id = values[1]  # ASSET_ID

        if hasattr(self, "btn_reserve"):
            self.btn_reserve.configure(state="normal")
        
        # Update the reservation info for this asset
        self.update_reservation_status()

    def update_reservation_status(self):
        """
        Show a short summary of any active reservations for the
        currently selected checked-out asset in the status label.
        """
        # If nothing is selected, clear the message
        if not getattr(self, "selected_active_asset_id", None):
            self.checkin_status.configure(text="", text_color="gray")
            return

        # Look up active reservations for this asset
        reservations = get_active_reservations_for_asset(self.selected_active_asset_id) or []

        if not reservations:
            # No active reservations
            self.checkin_status.configure(
                text="No active reservations for this asset.",
                text_color="gray",
            )
            return

        # Show info about the next reservation in line
        first = reservations[0]
        reserved_for = first["RESERVED_FOR"]
        target_date = first["TARGET_DATE"]

        # TARGET_DATE is stored as ISO like 'YYYY-MM-DDTHH:MM:SS'
        if target_date:
            target_date = target_date.split("T")[0]

        count = len(reservations)
        if target_date:
            msg = f"{count} active reservation(s). Next: {reserved_for} on {target_date}."
        else:
            msg = f"{count} active reservation(s). Next: {reserved_for} (no target date)."

        self.checkin_status.configure(text=msg, text_color="green")

    def open_reserve_window(self):
        """
        Open a small dialog to reserve the currently selected asset.
        The reservation is for a person and an optional target date.
        """
        if not self.selected_active_asset_id:
            self.checkin_status.configure(text="Select an asset to reserve.", text_color="red")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Reserve Asset - {self.selected_active_asset_id}")
        win.geometry("400x250")
        win.grab_set()  # modal behavior

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

        reserved_for_var = ctk.StringVar()
        target_date_var = ctk.StringVar()

        # Simple header showing which asset we are reserving
        ctk.CTkLabel(
            frame,
            text=f"Asset ID: {self.selected_active_asset_id}",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # "Reserved for" text field (who the asset is being reserved for)
        ctk.CTkLabel(frame, text="Reserved for:").grid(row=1, column=0, sticky="w", pady=4)
        ctk.CTkEntry(frame, textvariable=reserved_for_var).grid(
            row=1, column=1, sticky="ew", pady=4
        )

        # Optional target date for the reservation
        ctk.CTkLabel(frame, text="Desired date (YYYY-MM-DD):").grid(
            row=2, column=0, sticky="w", pady=4
        )
        ctk.CTkEntry(frame, textvariable=target_date_var).grid(
            row=2, column=1, sticky="ew", pady=4
        )

        status_lbl = ctk.CTkLabel(frame, text="")
        status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        def save_reservation():
            """
            Validate reservation fields and call services.create_reservation().
            """
            reserved_for = reserved_for_var.get().strip()
            target_date = target_date_var.get().strip() or None

            if not reserved_for:
                status_lbl.configure(text="Reserved for is required.", text_color="red")
                return

            try:
                create_reservation(
                    asset_id=self.selected_active_asset_id,
                    requested_by_emp_id=self.acting_emp_id,
                    reserved_for=reserved_for,
                    target_date=target_date,
                )
            except Exception as e:
                status_lbl.configure(text=str(e), text_color="red")
                return

            status_lbl.configure(text="Reservation saved.", text_color="green")
            
            # Update the main view's reservation summary
            self.update_reservation_status()
            
            # Close dialog shortly after success so the user sees the message
            win.after(800, win.destroy)

        # Bottom button row for the dialog
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(btn_frame, text="Save", command=save_reservation).pack(
            side="right", padx=(5, 0)
        )
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="gray", command=win.destroy
        ).pack(side="right")

    def refresh_active_checkouts(self):
        """
        Reload the 'Assets Currently Checked Out' table from the database.
        Also formats the check-out and due dates for easier reading.
        """
        # Clear existing rows
        for row in self.active_tree.get_children():
            self.active_tree.delete(row)

        # Might be None, so be safe
        txs = get_active_checkouts() or []

        for tx in txs:
            full_name = f"{tx['FIRST_NAME']} {tx['LAST_NAME']}"

            # Format "CHECK_OUT" as something readable like "Jan 01, 2025 01:23 PM"
            raw_dt = tx["CHECK_OUT"]
            pretty_dt = raw_dt
            if raw_dt:
                try:
                    dt_obj = datetime.fromisoformat(raw_dt)
                    pretty_dt = dt_obj.strftime("%b %d, %Y %I:%M %p")
                except ValueError:
                    # If parsing fails, just show the raw value
                    pretty_dt = raw_dt

            # Format the due date if present
            raw_due = tx["DUE_DATE"] if "DUE_DATE" in tx.keys() else None
            pretty_due = ""
            if raw_due:
                try:
                    due_obj = datetime.fromisoformat(raw_due)
                    pretty_due = due_obj.strftime("%b %d, %Y %I:%M %p")
                except ValueError:
                    pretty_due = raw_due

            # Insert row into the active checkouts Treeview
            self.active_tree.insert(
                "",
                "end",
                values=(
                    tx["TRANSACTION_NO"],
                    tx["ASSET_ID"],
                    tx["ASSET_DESCRIPTION"],
                    tx["CUST_EMAIL"],
                    full_name,
                    pretty_dt,   # CHECK_OUT
                    pretty_due,  # DUE_DATE
                ),
            )

    def do_checkin_selected(self):
        """
        Check in the currently selected checkout transaction:
          - Requires a selected row in the table
          - Calls services.checkin_transaction()
          - Refreshes both active + available asset tables
        """
        selected = self.active_tree.selection()
        if not selected:
            self.checkin_status.configure(text="No transaction selected.", text_color="red")
            return

        item_id = selected[0]
        values = self.active_tree.item(item_id, "values")
        transaction_no = values[0]

        try:
            checkin_transaction(transaction_no, acting_emp_id=self.acting_emp_id)
        except Exception as e:
            self.checkin_status.configure(text=str(e), text_color="red")
            return

        self.checkin_status.configure(text="Checked in successfully.", text_color="green")
        self.refresh_active_checkouts()
        self.refresh_available_assets()

