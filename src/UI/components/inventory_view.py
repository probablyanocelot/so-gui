try:
    import customtkinter
except ImportError:
    print("CustomTkinter is not installed. Please run:")
    print("pip install -r requirements.txt")
    exit(1)
from db import init_db
from UI.app import soGUIApp
from services import seed_default_admin

def main():
    """
    Initialize the database and start the main GUI loop.
    """
    # Make sure the database file and required tables exist
    init_db()
    seed_default_admin()

    # Create the main application window and start the event loop
    app = soGUIApp()
    app.mainloop()


class InventoryView(ctk.CTkFrame):
    # refactor: main view, search+table, selection handling
    
    """
    Main frame for the "Asset Inventory" screen.

    This view provides:0
      - A search box to filter assets by common fields
      - A Treeview showing asset details
      - Buttons for adding, editing, deleting, and logging maintenance
      - A thumbnail image preview for the selected asset
    """

    def __init__(self, master, acting_emp_id=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.acting_emp_id = acting_emp_id
        self.selected_asset_id = None

        # ---------------- Header row ----------------
        title_row = ctk.CTkFrame(self)
        title_row.pack(fill="x", padx=10, pady=(10, 5))

        title = ctk.CTkLabel(
            title_row,
            text="Asset Inventory",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(side="left")

        # ---------------- Search row ----------------
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search by ID, description, brand, model, location, department...",
        )
        search_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        search_btn = ctk.CTkButton(search_frame, text="Search", command=self.refresh_table)
        search_btn.pack(side="left")

        clear_btn = ctk.CTkButton(search_frame, text="Clear", command=self.clear_search)
        clear_btn.pack(side="left", padx=(5, 0))

        # ---------------- Table frame ----------------
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(
            table_frame,
            columns=(
                "ASSET_ID",
                "DESCRIPTION",
                "BRAND",
                "MODEL",
                "QUANTITY",
                "FUNDING_SOURCE",
                "WARRANTY_INFO",
                "SITE_NAME",
                "LOCATION_NAME",
                "DEPT_NAME",
                "CATEGORY_NAME",
                "AVAILABLE",
            ),
            show="headings",
        )

        headings = [
            ("ASSET_ID", "Asset ID", 100),
            ("DESCRIPTION", "Description", 180),
            ("BRAND", "Brand", 100),
            ("MODEL", "Model", 120),
            ("QUANTITY", "Quantity", 80),
            ("FUNDING_SOURCE", "Funding Source", 120),
            ("WARRANTY_INFO", "Warranty Info", 120),
            ("SITE_NAME", "Site", 100),
            ("LOCATION_NAME", "Location", 100),
            ("DEPT_NAME", "Dept", 100),
            ("CATEGORY_NAME", "Category", 120),
            ("AVAILABLE", "Available", 80),
        ]
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)

        self.tree.pack(expand=True, fill="both")

        # When an asset row is selected, update buttons + preview
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        
        # Initial load of table
        self.refresh_table()
        
            # ============================================================
    # Table / search
    # ============================================================

    def refresh_table(self):
        """
        Reload the asset table based on the current search term.
        Resets selection and disables asset-specific buttons.
        """
        self.selected_asset_id = None
        self.maint_btn.configure(state="disabled")
        self.edit_asset_btn.configure(state="disabled")
        self.delete_asset_btn.configure(state="disabled")
        self.status_label.configure(text="")

        # Clear current rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        term = self.search_var.get().strip() or None

        # Populate table with matching assets
        for asset in get_assets(term):
            self.tree.insert(
                "",
                "end",
                values=(
                    asset["ASSET_ID"],
                    asset["DESCRIPTION"],
                    asset["BRAND"],
                    asset["MODEL"],
                    asset["SITE_NAME"],
                    asset["LOCATION_NAME"],
                    asset["DEPT_NAME"],
                    asset["CATEGORY_NAME"],
                    asset["FUNDING_SOURCE"],
                    asset["QUANTITY"],
                    asset["WARRANTY_INFO"],
                    
                    "Yes" if asset["AVAILABLE"] else "No",
                ),
            )

        # Reset thumbnail preview when refreshing table
        
        self.selected_asset_id = None
        self.preview_image_label.configure(image=None, text="No image")
        if hasattr(self.preview_image_label, "image"):
            self.preview_image_label.image = None

    def clear_search(self):
        """
        Clear the search box and reload the full asset list.
        """
        self.search_var.set("")
        self.refresh_table()

    def on_tree_select(self, event):
        """
        Handle row selection in the asset table:
          - Track which asset is selected
          - Enable buttons that require a selected asset
          - Update the image thumbnail preview
        """
        selected = self.tree.selection()
        if not selected:
            self.selected_asset_id = None
            self.maint_btn.configure(state="disabled")
            self.edit_asset_btn.configure(state="disabled")
            self.delete_asset_btn.configure(state="disabled")
            self.status_label.configure(text="")
            return

        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        # Column order: ASSET_ID, DESCRIPTION, ...
        self.selected_asset_id = values[0]

        self.maint_btn.configure(state="normal")
        self.edit_asset_btn.configure(state="normal")
        self.delete_asset_btn.configure(state="normal")
        self.status_label.configure(text=f"Selected asset: {self.selected_asset_id}")

        # Update thumbnail preview when selection changes
        self.update_image_preview()


if __name__ == "__main__":
    # Only run the app if this file is executed directly
    main()
