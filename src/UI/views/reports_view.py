"""
soGUI — Reports View

Description:
    This file defines the ReportsView, which is responsible for:
      - Inventory report (read-only view of all assets, with search + CSV export)
      - Audit log report (filterable by action, asset ID, employee, and date range)
      - Maintenance log report (filterable by asset and date range)

    The actual data is provided by service-layer functions in services.py.
    This view focuses on the UI layout, filtering inputs, and exporting
    visible results to CSV when needed.
"""

import customtkinter as ctk
from tkinter import ttk, filedialog
from datetime import datetime

from services import get_assets, get_audit_log, get_maintenance_log, get_inventory_report


class ReportsView(ctk.CTkFrame):
    """
    Main reports screen, containing three tabs:

      - Inventory Report
      - Audit Log
      - Maintenance Log

    Args:
        master: Parent widget.
        acting_emp_id: Employee ID of the user viewing reports
                       (kept for consistency even if not used now).
    """

    def __init__(self, master, acting_emp_id=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.acting_emp_id = acting_emp_id

        # Title label at the top of the reports area
        title = ctk.CTkLabel(
            self,
            text="Reports",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(pady=(10, 5))

        # Top-level tab control (Inventory / Audit / Maintenance)
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.inv_tab = self.tabs.add("Inventory Report")
        self.audit_tab = self.tabs.add("Audit Log")
        self.maint_tab = self.tabs.add("Maintenance Log")

        # Build each tab UI
        self._build_inventory_tab()
        self._build_audit_tab()
        self._build_maintenance_tab()

    # ============================================================
    # Helper: export any Treeview to CSV
    # ============================================================

    def export_tree_to_csv(self, tree, default_name):
        """
        Export the current contents of a Treeview to a CSV file.

        Args:
            tree: ttk.Treeview instance containing the data.
            default_name: Suggested filename for the Save As dialog.
        """
        file_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return  # user canceled

        import csv

        columns = tree["columns"]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header row
            writer.writerow(columns)
            # Data rows
            for row_id in tree.get_children():
                values = tree.item(row_id, "values")
                writer.writerow(values)

     # ============================================================
    # INVENTORY REPORT TAB
    # ============================================================

        # ============================================================
    # INVENTORY REPORT TAB
    # ============================================================

    def _build_inventory_tab(self):
        """
        Build the Inventory Report tab UI.

        Includes:
          - Text search
          - 'Filter by' dropdown (which column to search)
          - Purchase date range (from / to)
          - Treeview listing inventory
        """
        parent = self.inv_tab  # use the tab as the parent

        # ---------- Filter Bar ----------
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.pack(fill="x", padx=10, pady=10)

        # Search term input
        self.inv_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.inv_search_var,
            placeholder_text="Search inventory...",
            width=220,
        )
        search_entry.pack(side="left", padx=(0, 6))

        # Filter by dropdown
        self.inv_filter_field_var = ctk.StringVar(value="Any")

        filter_label = ctk.CTkLabel(filter_frame, text="Filter by:")
        filter_label.pack(side="left", padx=(4, 2))

        self.inv_filter_field_combo = ctk.CTkComboBox(
            filter_frame,
            width=150,
            variable=self.inv_filter_field_var,
            values=[
                "Any",
                "Asset ID",
                "Description",
                "Brand",
                "Model",
                "Serial",
                "Purchase Date",
                "Cost",
                "Site",
                "Location",
                "Department",
                "Category",
            ],
            state="readonly",
        )
        self.inv_filter_field_combo.pack(side="left", padx=(0, 12))

        # Purchase date range
        self.inv_start_date_var = ctk.StringVar()
        self.inv_end_date_var = ctk.StringVar()

        date_label = ctk.CTkLabel(filter_frame, text="Purchased from:")
        date_label.pack(side="left", padx=(0, 2))

        start_entry = ctk.CTkEntry(
            filter_frame,
            width=100,
            textvariable=self.inv_start_date_var,
            placeholder_text="YYYY-MM-DD",
        )
        start_entry.pack(side="left", padx=(0, 4))

        to_label = ctk.CTkLabel(filter_frame, text="to:")
        to_label.pack(side="left", padx=(0, 2))

        end_entry = ctk.CTkEntry(
            filter_frame,
            width=100,
            textvariable=self.inv_end_date_var,
            placeholder_text="YYYY-MM-DD",
        )
        end_entry.pack(side="left", padx=(0, 10))

        # Search / Clear buttons
        search_btn = ctk.CTkButton(
            filter_frame,
            text="Search",
            width=80,
            command=self.refresh_inventory_table,
        )
        search_btn.pack(side="left", padx=(0, 5))

        clear_btn = ctk.CTkButton(
            filter_frame,
            text="Clear",
            width=80,
            fg_color="gray",
            command=self.clear_inventory_filter,
        )
        clear_btn.pack(side="left")

        # ---------- Treeview ----------
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = (
            "ASSET_ID",
            "DESCRIPTION",
            "BRAND",
            "MODEL",
            "SERIAL",
            "SITE_NAME",
            "LOCATION_NAME",
            "DEPT_NAME",
            "CATEGORY_NAME",
            "AVAILABLE",
            "PURCHASE_DATE",
            "COST",
        )

        self.inv_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        # Set column headings
        self.inv_tree.heading("ASSET_ID", text="Asset ID")
        self.inv_tree.heading("DESCRIPTION", text="Description")
        self.inv_tree.heading("BRAND", text="Brand")
        self.inv_tree.heading("MODEL", text="Model")
        self.inv_tree.heading("SERIAL", text="Serial")
        self.inv_tree.heading("SITE_NAME", text="Site")
        self.inv_tree.heading("LOCATION_NAME", text="Location")
        self.inv_tree.heading("DEPT_NAME", text="Department")
        self.inv_tree.heading("CATEGORY_NAME", text="Category")
        self.inv_tree.heading("AVAILABLE", text="Available")
        self.inv_tree.heading("PURCHASE_DATE", text="Purchase Date")
        self.inv_tree.heading("COST", text="Cost")

        # Column widths (tweak as you like)
        self.inv_tree.column("ASSET_ID", width=90, anchor="w")
        self.inv_tree.column("DESCRIPTION", width=160, anchor="w")
        self.inv_tree.column("BRAND", width=100, anchor="w")
        self.inv_tree.column("MODEL", width=100, anchor="w")
        self.inv_tree.column("SERIAL", width=120, anchor="w")
        self.inv_tree.column("SITE_NAME", width=100, anchor="w")
        self.inv_tree.column("LOCATION_NAME", width=110, anchor="w")
        self.inv_tree.column("DEPT_NAME", width=110, anchor="w")
        self.inv_tree.column("CATEGORY_NAME", width=100, anchor="w")
        self.inv_tree.column("AVAILABLE", width=70, anchor="center")
        self.inv_tree.column("PURCHASE_DATE", width=100, anchor="center")
        self.inv_tree.column("COST", width=80, anchor="e")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.inv_tree.yview)
        self.inv_tree.configure(yscrollcommand=vsb.set)

        self.inv_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # ---------- Status bar + Export ----------
        bottom = ctk.CTkFrame(parent)
        bottom.pack(fill="x", padx=10, pady=(0, 8))

        self.inv_status = ctk.CTkLabel(bottom, text="Inventory report ready.")
        self.inv_status.pack(side="left")

        btn_export = ctk.CTkButton(
            bottom,
            text="Export to CSV",
            command=self.export_inventory_report,
        )
        btn_export.pack(side="right")

        # Initial load
        self.refresh_inventory_table()

    def refresh_inventory_table(self):
        """
        Reload the inventory report table using:
          - search term
          - filter field (column selection)
          - purchase date range
        """
        # Clear current rows
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)

        # Gather filters
        search_term = self.inv_search_var.get().strip() or None

        filter_field = self.inv_filter_field_var.get()
        if filter_field == "Any":
            filter_field = None

        start_date = self.inv_start_date_var.get().strip() or None
        end_date = self.inv_end_date_var.get().strip() or None

        # Query the database
        rows = get_inventory_report(
            search_term=search_term,
            filter_field=filter_field,
            start_date=start_date,
            end_date=end_date,
        )

        count = 0
        for asset in rows:
            self.inv_tree.insert(
                "",
                "end",
                values=(
                    asset["ASSET_ID"],
                    asset["DESCRIPTION"],
                    asset["BRAND"],
                    asset["MODEL"],
                    asset["SERIAL"],
                    asset["SITE_NAME"],
                    asset["LOCATION_NAME"],
                    asset["DEPT_NAME"],
                    asset["CATEGORY_NAME"],
                    "Yes" if asset["AVAILABLE"] else "No",
                    asset["PURCHASE_DATE"] or "",
                    asset["COST"] if asset["COST"] is not None else "",
                ),
            )
            count += 1

        self.inv_status.configure(text=f"{count} asset(s) listed.")

    def clear_inventory_filter(self):
        """
        Reset all filters on the inventory report and reload the table.
        """
        self.inv_search_var.set("")
        if hasattr(self, "inv_filter_field_var"):
            self.inv_filter_field_var.set("Any")
        if hasattr(self, "inv_start_date_var"):
            self.inv_start_date_var.set("")
        if hasattr(self, "inv_end_date_var"):
            self.inv_end_date_var.set("")
        self.refresh_inventory_table()


    def export_inventory_report(self):
        """
        Export the current Inventory Report to a CSV file.
        """
        self.export_tree_to_csv(self.inv_tree, "inventory_report.csv")

    # ============================================================
    # Audit Log tab
    # ============================================================

    def _build_audit_tab(self):
        """
        Build the layout for the Audit Log tab.
        Includes filters for:
          - Action
          - Asset ID
          - Employee ID
          - Start date / End date
        And a Treeview to display matching audit entries.
        """
        outer = ctk.CTkFrame(self.audit_tab)
        outer.pack(expand=True, fill="both", padx=10, pady=10)

        # Filter area
        filter_frame = ctk.CTkFrame(outer)
        filter_frame.pack(fill="x", pady=(0, 10))

        lbl = ctk.CTkLabel(filter_frame, text="Audit Log (all actions)")
        lbl.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        # Action filter
        ctk.CTkLabel(filter_frame, text="Action:").grid(
            row=0, column=1, padx=(5, 0), pady=5, sticky="e"
        )
        self.audit_action_var = ctk.StringVar()
        action_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.audit_action_var,
            width=120,
            placeholder_text="e.g. CHECKOUT",
        )
        action_entry.grid(row=0, column=2, padx=(2, 10), pady=5, sticky="w")

        # Asset filter
        ctk.CTkLabel(filter_frame, text="Asset ID:").grid(
            row=0, column=3, padx=(5, 0), pady=5, sticky="e"
        )
        self.audit_asset_var = ctk.StringVar()
        asset_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.audit_asset_var,
            width=110,
        )
        asset_entry.grid(row=0, column=4, padx=(2, 10), pady=5, sticky="w")

        # Employee filter
        ctk.CTkLabel(filter_frame, text="Employee ID:").grid(
            row=0, column=5, padx=(5, 0), pady=5, sticky="e"
        )
        self.audit_emp_var = ctk.StringVar()
        emp_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.audit_emp_var,
            width=110,
        )
        emp_entry.grid(row=0, column=6, padx=(2, 10), pady=5, sticky="w")

        # Date range
        ctk.CTkLabel(filter_frame, text="Start date (YYYY-MM-DD):").grid(
            row=1, column=1, padx=(5, 0), pady=5, sticky="e"
        )
        self.audit_start_var = ctk.StringVar()
        start_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.audit_start_var,
            width=120,
        )
        start_entry.grid(row=1, column=2, padx=(2, 10), pady=5, sticky="w")

        ctk.CTkLabel(filter_frame, text="End date (YYYY-MM-DD):").grid(
            row=1, column=3, padx=(5, 0), pady=5, sticky="e"
        )
        self.audit_end_var = ctk.StringVar()
        end_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.audit_end_var,
            width=120,
        )
        end_entry.grid(row=1, column=4, padx=(2, 10), pady=5, sticky="w")

        btn_filter = ctk.CTkButton(
            filter_frame,
            text="Apply Filter",
            command=self.refresh_audit_table,
        )
        btn_filter.grid(row=0, column=7, padx=(5, 0), pady=5, sticky="w")

        btn_clear = ctk.CTkButton(
            filter_frame,
            text="Clear",
            command=self.clear_audit_filter,
        )
        btn_clear.grid(row=0, column=8, padx=(5, 0), pady=5, sticky="w")

        # Table area
        table_frame = ctk.CTkFrame(outer)
        table_frame.pack(expand=True, fill="both")

        self.audit_tree = ttk.Treeview(
            table_frame,
            columns=(
                "LOG_NO",
                "LOG_DATE",
                "ACTION",
                "ASSET_ID",
                "ASSET_DESCRIPTION",
                "EMP_ID",
                "EMP_NAME",
                "DETAILS",
            ),
            show="headings",
        )

        columns = [
            ("LOG_NO", "Log #", 60),
            ("LOG_DATE", "Date / Time", 150),
            ("ACTION", "Action", 100),
            ("ASSET_ID", "Asset ID", 90),
            ("ASSET_DESCRIPTION", "Asset Description", 200),
            ("EMP_ID", "Employee ID", 100),
            ("EMP_NAME", "Employee Name", 150),
            ("DETAILS", "Details", 300),
        ]
        for col, text, width in columns:
            self.audit_tree.heading(col, text=text)
            self.audit_tree.column(col, width=width)

        self.audit_tree.pack(expand=True, fill="both")

        # Bottom: status + export
        bottom = ctk.CTkFrame(outer)
        bottom.pack(fill="x", pady=(5, 0))

        self.audit_status = ctk.CTkLabel(bottom, text="")
        self.audit_status.pack(side="left")

        btn_export = ctk.CTkButton(
            bottom,
            text="Export to CSV",
            command=self.export_audit_log,
        )
        btn_export.pack(side="right")

        # Initial load
        self.refresh_audit_table()

    def clear_audit_filter(self):
        """
        Clear all audit filters and reload the full audit log.
        """
        self.audit_action_var.set("")
        self.audit_asset_var.set("")
        self.audit_emp_var.set("")
        self.audit_start_var.set("")
        self.audit_end_var.set("")
        self.refresh_audit_table()

    def refresh_audit_table(self):
        """
        Refresh the audit Treeview using the current filter values.
        """
        for row in self.audit_tree.get_children():
            self.audit_tree.delete(row)

        action = self.audit_action_var.get().strip() or None
        asset_id = self.audit_asset_var.get().strip() or None
        emp_id = self.audit_emp_var.get().strip() or None
        start_date = self.audit_start_var.get().strip() or None
        end_date = self.audit_end_var.get().strip() or None

        try:
            rows = get_audit_log(
                action=action,
                asset_id=asset_id,
                emp_id=emp_id,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            self.audit_status.configure(
                text=f"Error loading audit log: {e}",
                text_color="red",
            )
            return

        count = 0
        for r in rows:
            count += 1

            # Reformat LOG_DATE into something human-friendly
            raw_dt = r["LOG_DATE"]
            pretty_dt = raw_dt
            if raw_dt:
                try:
                    dt_obj = datetime.fromisoformat(raw_dt)
                    pretty_dt = dt_obj.strftime("%b %d, %Y %I:%M %p")
                except ValueError:
                    pretty_dt = raw_dt

            # Combine first/last name for display
            emp_name = (r["FIRST_NAME"] or "") + " " + (r["LAST_NAME"] or "")
            emp_name = emp_name.strip()

            self.audit_tree.insert(
                "",
                "end",
                values=(
                    r["LOG_NO"],
                    pretty_dt,
                    r["ACTION"],
                    r["ASSET_ID"],
                    r["ASSET_DESCRIPTION"],
                    r["EMP_ID"],
                    emp_name,
                    r["DETAILS"],
                ),
            )

        self.audit_status.configure(
            text=f"Showing {count} audit entr{'y' if count == 1 else 'ies'}.",
            text_color="white",
        )

    def export_audit_log(self):
        """
        Export the current Audit Log view to CSV.
        """
        self.export_tree_to_csv(self.audit_tree, "audit_log.csv")

    # ============================================================
    # Maintenance Log tab
    # ============================================================

    def _build_maintenance_tab(self):
        """
        Build the layout for the Maintenance Log tab.
        Includes:
          - Optional asset and date range filters
          - Read-only Treeview for maintenance entries
        """
        outer = ctk.CTkFrame(self.maint_tab)
        outer.pack(expand=True, fill="both", padx=10, pady=10)

        # Filter row
        filter_frame = ctk.CTkFrame(outer)
        filter_frame.pack(fill="x", pady=(0, 10))

        lbl = ctk.CTkLabel(
            filter_frame,
            text="Maintenance entries (logged via Inventory → Add Maintenance Entry)",
        )
        lbl.grid(row=0, column=0, columnspan=4, sticky="w")

        # Asset filter
        ctk.CTkLabel(filter_frame, text="Asset ID:").grid(
            row=1, column=0, padx=(0, 5), pady=5, sticky="e"
        )
        self.maint_asset_filter_var = ctk.StringVar()
        asset_filter_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.maint_asset_filter_var,
            width=140,
            placeholder_text="optional",
        )
        asset_filter_entry.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="w")

        # Date range fields
        ctk.CTkLabel(filter_frame, text="Start date (YYYY-MM-DD):").grid(
            row=1, column=2, padx=(5, 0), pady=5, sticky="e"
        )
        self.maint_start_var = ctk.StringVar()
        start_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.maint_start_var,
            width=130,
        )
        start_entry.grid(row=1, column=3, padx=(2, 10), pady=5, sticky="w")

        ctk.CTkLabel(filter_frame, text="End date (YYYY-MM-DD):").grid(
            row=1, column=4, padx=(5, 0), pady=5, sticky="e"
        )
        self.maint_end_var = ctk.StringVar()
        end_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.maint_end_var,
            width=130,
        )
        end_entry.grid(row=1, column=5, padx=(2, 10), pady=5, sticky="w")

        btn_filter = ctk.CTkButton(
            filter_frame,
            text="Apply Filter",
            command=self.refresh_maintenance_table,
            width=100,
        )
        btn_filter.grid(row=1, column=6, padx=(5, 0), pady=5, sticky="w")

        btn_clear = ctk.CTkButton(
            filter_frame,
            text="Show All",
            command=self.clear_maintenance_filter,
            width=90,
        )
        btn_clear.grid(row=1, column=7, padx=(5, 0), pady=5, sticky="w")

        # Table area
        table_frame = ctk.CTkFrame(outer)
        table_frame.pack(expand=True, fill="both")

        self.maint_tree = ttk.Treeview(
            table_frame,
            columns=(
                "LOG_NO",
                "LOG_DATE",
                "ASSET_ID",
                "ASSET_DESCRIPTION",
                "EMP_ID",
                "EMP_NAME",
                "DETAILS",
            ),
            show="headings",
        )

        columns = [
            ("LOG_NO", "Log #", 60),
            ("LOG_DATE", "Date / Time", 150),
            ("ASSET_ID", "Asset ID", 90),
            ("ASSET_DESCRIPTION", "Asset Description", 200),
            ("EMP_ID", "Employee ID", 100),
            ("EMP_NAME", "Employee Name", 150),
            ("DETAILS", "Details", 300),
        ]
        for col, text, width in columns:
            self.maint_tree.heading(col, text=text)
            self.maint_tree.column(col, width=width)

        self.maint_tree.pack(expand=True, fill="both")

        # Bottom: status + export
        bottom = ctk.CTkFrame(outer)
        bottom.pack(fill="x", pady=(5, 0))

        self.maint_status = ctk.CTkLabel(bottom, text="")
        self.maint_status.pack(side="left")

        btn_export = ctk.CTkButton(
            bottom,
            text="Export to CSV",
            command=self.export_maintenance_log,
        )
        btn_export.pack(side="right")

        # Initial load
        self.refresh_maintenance_table()

    def clear_maintenance_filter(self):
        """
        Clear all maintenance filters and reload all entries.
        """
        self.maint_asset_filter_var.set("")
        self.maint_start_var.set("")
        self.maint_end_var.set("")
        self.refresh_maintenance_table()

    def refresh_maintenance_table(self):
        """
        Reload the maintenance Treeview based on the current filters.
        """
        for row in self.maint_tree.get_children():
            self.maint_tree.delete(row)

        asset_filter = self.maint_asset_filter_var.get().strip() or None
        start_date = self.maint_start_var.get().strip() or None
        end_date = self.maint_end_var.get().strip() or None

        try:
            rows = get_maintenance_log(
                asset_id=asset_filter,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            self.maint_status.configure(
                text=f"Error loading maintenance log: {e}",
                text_color="red",
            )
            return

        count = 0
        for r in rows:
            count += 1

            # Make LOG_DATE more readable
            raw_dt = r["LOG_DATE"]
            pretty_dt = raw_dt
            if raw_dt:
                try:
                    dt_obj = datetime.fromisoformat(raw_dt)
                    pretty_dt = dt_obj.strftime("%b %d,  %Y %I:%M %p")
                except ValueError:
                    pretty_dt = raw_dt

            # Combine first/last name for display
            emp_name = (r["FIRST_NAME"] or "") + " " + (r["LAST_NAME"] or "")
            emp_name = emp_name.strip()

            self.maint_tree.insert(
                "",
                "end",
                values=(
                    r["LOG_NO"],
                    pretty_dt,
                    r["ASSET_ID"],
                    r["ASSET_DESCRIPTION"],
                    r["EMP_ID"],
                    emp_name,
                    r["DETAILS"],
                ),
            )

        if asset_filter or start_date or end_date:
            self.maint_status.configure(
                text=f"Showing {count} maintenance entr{'y' if count == 1 else 'ies'} (filtered).",
                text_color="white",
            )
        else:
            self.maint_status.configure(
                text=f"Showing {count} maintenance entr{'y' if count == 1 else 'ies'} (all assets).",
                text_color="white",
            )

    def export_maintenance_log(self):
        """
        Export the current Maintenance Log view to CSV.
        """
        self.export_tree_to_csv(self.maint_tree, "maintenance_log.csv")


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
    root.title("ReportsView debug")
    root.geometry("1000x700")

    view = ReportsView(root, acting_emp_id="admin")
    view.pack(expand=True, fill="both")

    root.mainloop()