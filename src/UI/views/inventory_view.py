import customtkinter as ctk
from services import get_assets, get_asset, delete_asset

try:
    import customtkinter
except ImportError:
    print("CustomTkinter is not installed. Please run:")
    print("pip install -r requirements.txt")
    exit(1)
from db import init_db
# from UI.app import soGUIApp
# from services import seed_default_admin

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
        
        
                # ---------------- Bottom action buttons ----------------
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.add_asset_btn = ctk.CTkButton(
            bottom_frame,
            text="Add Asset",
            command=self.open_add_asset_window,
        )
        self.add_asset_btn.pack(side="right", padx=10)

        self.edit_asset_btn = ctk.CTkButton(
            bottom_frame,
            text="Edit Asset",
            state="disabled",
            command=self.open_edit_asset_window,
        )
        self.edit_asset_btn.pack(side="right", padx=(10, 0))

        self.delete_asset_btn = ctk.CTkButton(
            bottom_frame,
            text="Delete Asset",
            state="disabled",
            fg_color="#b91c1c",  # red-ish tone
            hover_color="#ef4444",
            command=self.delete_selected_asset,
        )
        self.delete_asset_btn.pack(side="right", padx=(10, 0))

        self.maint_btn = ctk.CTkButton(
            bottom_frame,
            text="Add Maintenance Entry",
            state="disabled",
            command=self.open_maintenance_window,
        )
        self.maint_btn.pack(side="right")

        self.status_label = ctk.CTkLabel(bottom_frame, text="")
        self.status_label.pack(side="left", padx=10)


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
        
        
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="x", padx=10, pady=(0, 10))

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Image preview (click to open full size):",
            anchor="w",
        )
        preview_label.pack(anchor="w")

        self.preview_image_label = ctk.CTkLabel(
            preview_frame,
            text="No image",
            width=150,
            height=150,
            corner_radius=8,
        )
        self.preview_image_label.pack(anchor="w", pady=(4, 0))
        self.preview_image_label.bind("<Button-1>", self.open_full_image_window)
        
        # Initial load of table
        self.refresh_table()
        
        
        
            # ============================================================
    # Table / search
    # ============================================================
    def open_add_asset_window(self):
        """
        Open a dialog for creating a brand new asset.
        Only Asset ID is required; everything else is optional.
        """
        win = ctk.CTkToplevel(self)
        win.title("Add Asset")
        win.geometry("500x550")
        win.grab_set()

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)
    
    def open_edit_asset_window(self):
        """
        Open a dialog with the selected asset's info prefilled for editing.
        """
        if not self.selected_asset_id:
            self.status_label.configure(text="Please select an asset to edit.", text_color="red")
            return

        row = get_asset(self.selected_asset_id)
        if not row:
            self.status_label.configure(text="Selected asset not found.", text_color="red")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Edit Asset - {self.selected_asset_id}")
        win.geometry("500x550")
        win.grab_set()

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

    def open_maintenance_window(self):
        """
        Open a dialog to add a maintenance note for the selected asset.
        The note is stored via add_maintenance_entry in the service layer.
        """
        if not self.selected_asset_id:
            self.status_label.configure(text="Please select an asset first.", text_color="red")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Add Maintenance Entry - {self.selected_asset_id}")
        win.geometry("500x350")
        win.grab_set()

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

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
        
    def open_full_image_window(self, event=None):
        """
        Open a larger view of the selected asset's image in a new pop-up window.
        """
        if not self.selected_asset_id:
            return

        row = get_asset(self.selected_asset_id)
        if not row:
            return

        img_path = row["IMAGE_PATH"]
        if not img_path:
            return

        try:
            pil_img = Image.open(img_path)
        except Exception:
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Image - {self.selected_asset_id}")
        win.geometry("650x650")
        win.grab_set()

        # Resize image to fit nicely in the window
        max_size = (600, 600)
        pil_img.thumbnail(max_size)

        full_image = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=pil_img.size,
        )

        img_label = ctk.CTkLabel(win, image=full_image, text="")
        img_label.image = full_image  # keep a reference on the label
        img_label.pack(padx=20, pady=20)

    def delete_selected_asset(self):
        """
        Delete the currently selected asset after a confirmation dialog.
        """
        if not self.selected_asset_id:
            self.status_label.configure(text="Please select an asset to delete.", text_color="red")
            return

        answer = messagebox.askyesno(
            "Delete Asset",
            f"Are you sure you want to delete asset '{self.selected_asset_id}'?\nThis cannot be undone.",
        )
        if not answer:
            return

        try:
            delete_asset(self.selected_asset_id, acting_emp_id=self.acting_emp_id)
        except Exception as e:
            self.status_label.configure(text=f"Error deleting asset: {e}", text_color="red")
            return

        self.status_label.configure(
            text=f"Deleted asset: {self.selected_asset_id}",
            text_color="white",
        )
        self.refresh_table()



if __name__ == "__main__":
    # This block allows us to run this view in isolation for testing/debugging purposes.
    import os
    import sys
    
    from tkinter import ttk
    

    # Make src/ importable when running this file directly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

    import customtkinter as ctk
    from db import init_db
    from database import seed_default_admin

    # Optional: initialize DB state for view testing
    init_db()
    seed_default_admin()

    root = ctk.CTk()
    root.title("InventoryView debug")
    root.geometry("1000x700")

    view = InventoryView(root, acting_emp_id="admin")
    view.pack(expand=True, fill="both")

    root.mainloop()