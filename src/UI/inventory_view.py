"""
soGUI — Inventory View

Description:
    This file defines the InventoryView, which is responsible for:
      - Listing assets in a searchable table
      - Showing a small thumbnail image preview for the selected asset
      - Adding new assets
      - Editing existing assets
      - Deleting assets
      - Adding maintenance entries for a selected asset

    All database operations are delegated to services.py so the UI
    stays focused on layout and user interaction.
"""

import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from PIL import Image

from services import (
    get_assets,
    create_asset,
    add_maintenance_entry,
    get_asset,
    update_asset,
    delete_asset,
)


class InventoryView(ctk.CTkFrame):
    """
    Main frame for the "Asset Inventory" screen.

    This view provides:
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

        # ---------------- Image preview area ----------------
        # Keep a reference to the CTkImage so it doesn't get garbage-collected
        self.preview_ctkimage = None

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

        # Clicking the thumbnail opens a larger image window
        self.preview_image_label.bind("<Button-1>", self.open_full_image_window)

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

    # ============================================================
    # Image preview
    # ============================================================

    def update_image_preview(self):
        """
        Load a small thumbnail for the selected asset, if it has an IMAGE_PATH.

        This version:
        - clears the label's visible image,
        - loads the image (if present),
        - creates a CTkImage thumbnail,
        - and stores a reference on the label to prevent garbage collection.
        """

        # Clear the visible image/text (safe even if an old image exists)
        self.preview_image_label.configure(image=None, text="No image")

        # If nothing is selected, we're done
        if not getattr(self, "selected_asset_id", None):
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
            self.preview_image_label.configure(text="Could not load image")
            return

        # Create thumbnail (e.g., max 150x150)
        max_size = (150, 150)
        pil_img.thumbnail(max_size)

        # Create CTkImage thumbnail
        thumb = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=pil_img.size,
        )

        # Attach the CTkImage to the label AND keep a reference on the label
        self.preview_image_label.configure(image=thumb, text="")
        self.preview_image_label.image = thumb  # set image to thumb




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

    # ============================================================
    # Add asset dialog
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

        # Form state variables
        self.asset_id_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.brand_var = ctk.StringVar()
        self.model_var = ctk.StringVar()
        self.serial_var = ctk.StringVar()
        self.purchase_date_var = ctk.StringVar()
        self.cost_var = ctk.StringVar()
        self.site_var = ctk.StringVar()
        self.location_var = ctk.StringVar()
        self.dept_var = ctk.StringVar()
        self.category_var = ctk.StringVar()
        self.image_path_var = ctk.StringVar()
        self.available_var = ctk.BooleanVar(value=True)

        def add_row(row, label_text, var):
            lbl = ctk.CTkLabel(frame, text=label_text)
            lbl.grid(row=row, column=0, sticky="w", pady=4)
            ent = ctk.CTkEntry(frame, textvariable=var)
            ent.grid(row=row, column=1, sticky="ew", pady=4)

        add_row(0, "Asset ID *", self.asset_id_var)
        add_row(1, "Description", self.description_var)
        add_row(2, "Brand", self.brand_var)
        add_row(3, "Model", self.model_var)
        add_row(4, "Serial", self.serial_var)
        add_row(5, "Purchase Date", self.purchase_date_var)
        add_row(6, "Cost", self.cost_var)
        add_row(7, "Site", self.site_var)
        add_row(8, "Location", self.location_var)
        add_row(9, "Department", self.dept_var)
        add_row(10, "Category", self.category_var)

        # Row 11: Image path + Browse button
        lbl_img = ctk.CTkLabel(frame, text="Image path / URL")
        lbl_img.grid(row=11, column=0, sticky="w", pady=4)

        img_row_frame = ctk.CTkFrame(frame)
        img_row_frame.grid(row=11, column=1, sticky="ew", pady=4)
        img_row_frame.grid_columnconfigure(0, weight=1)

        img_entry = ctk.CTkEntry(img_row_frame, textvariable=self.image_path_var)
        img_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        def browse_image():
            """
            Let the user select a local image file and store the path.
            """
            file_path = filedialog.askopenfilename(
                title="Select image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*"),
                ],
            )
            if file_path:
                self.image_path_var.set(file_path)

        browse_btn = ctk.CTkButton(
            img_row_frame,
            text="Browse...",
            width=80,
            command=browse_image,
        )
        browse_btn.grid(row=0, column=1)

        # Row 12: Available checkbox
        chk = ctk.CTkCheckBox(frame, text="Available", variable=self.available_var)
        chk.grid(row=12, column=0, columnspan=2, sticky="w", pady=6)

        # Buttons at bottom of dialog
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(btn_frame, text="Save", command=lambda: self.save_asset(win))
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", command=win.destroy)
        cancel_btn.pack(side="right")

    def save_asset(self, window):
        """
        Read the add-asset form, validate, and create a new asset record.
        Closes the dialog and refreshes the table on success.
        """
        asset_id = self.asset_id_var.get().strip()
        if not asset_id:
            print("Asset ID is required.")
            return

        description = self.description_var.get().strip() or None
        brand = self.brand_var.get().strip() or None
        model = self.model_var.get().strip() or None
        serial = self.serial_var.get().strip() or None
        purchase_date = self.purchase_date_var.get().strip() or None
        site = self.site_var.get().strip() or None
        location = self.location_var.get().strip() or None
        dept = self.dept_var.get().strip() or None
        category = self.category_var.get().strip() or None
        image_path = self.image_path_var.get().strip() or None
        available = self.available_var.get()

        cost_value = None
        cost_str = self.cost_var.get().strip()
        if cost_str:
            try:
                cost_value = float(cost_str)
            except ValueError:
                print("Cost must be a number.")
                return

        try:
            create_asset(
                asset_id=asset_id,
                description=description,
                brand=brand,
                model=model,
                serial=serial,
                purchase_date=purchase_date,
                cost=cost_value,
                site_name=site,
                location_name=location,
                dept_name=dept,
                category_name=category,
                image_path=image_path,
                available=available,
                acting_emp_id=self.acting_emp_id,
            )
        except Exception as e:
            print("Error creating asset:", e)
            return

        window.destroy()
        self.refresh_table()

    # ============================================================
    # Edit asset dialog
    # ============================================================

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

        # Form variables, prefilled from DB
        self.asset_id_var = ctk.StringVar(value=row["ASSET_ID"])
        self.description_var = ctk.StringVar(value=row["DESCRIPTION"] or "")
        self.brand_var = ctk.StringVar(value=row["BRAND"] or "")
        self.model_var = ctk.StringVar(value=row["MODEL"] or "")
        self.serial_var = ctk.StringVar(value=row["SERIAL"] or "")
        self.purchase_date_var = ctk.StringVar(value=row["PURCHASE_DATE"] or "")
        self.cost_var = ctk.StringVar(
            value=str(row["COST"]) if row["COST"] is not None else ""
        )
        self.site_var = ctk.StringVar(value=row["SITE_NAME"] or "")
        self.location_var = ctk.StringVar(value=row["LOCATION_NAME"] or "")
        self.dept_var = ctk.StringVar(value=row["DEPT_NAME"] or "")
        self.category_var = ctk.StringVar(value=row["CATEGORY_NAME"] or "")
        self.image_path_var = ctk.StringVar(value=row["IMAGE_PATH"] or "")
        self.available_var = ctk.BooleanVar(value=bool(row["AVAILABLE"]))

        def add_row(row_index, label_text, var, readonly=False):
            lbl = ctk.CTkLabel(frame, text=label_text)
            lbl.grid(row=row_index, column=0, sticky="w", pady=4)
            ent = ctk.CTkEntry(frame, textvariable=var)
            if readonly:
                ent.configure(state="disabled")
            ent.grid(row=row_index, column=1, sticky="ew", pady=4)

        # Asset ID stays read-only
        add_row(0, "Asset ID", self.asset_id_var, readonly=True)
        add_row(1, "Description", self.description_var)
        add_row(2, "Brand", self.brand_var)
        add_row(3, "Model", self.model_var)
        add_row(4, "Serial", self.serial_var)
        add_row(5, "Purchase Date", self.purchase_date_var)
        add_row(6, "Cost", self.cost_var)
        add_row(7, "Site", self.site_var)
        add_row(8, "Location", self.location_var)
        add_row(9, "Department", self.dept_var)
        add_row(10, "Category", self.category_var)

        # Row 11: Image path + Browse button
        lbl_img = ctk.CTkLabel(frame, text="Image path / URL")
        lbl_img.grid(row=11, column=0, sticky="w", pady=4)

        img_row_frame = ctk.CTkFrame(frame)
        img_row_frame.grid(row=11, column=1, sticky="ew", pady=4)
        img_row_frame.grid_columnconfigure(0, weight=1)

        img_entry = ctk.CTkEntry(img_row_frame, textvariable=self.image_path_var)
        img_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        def browse_image_edit():
            """
            Let the user select a new image file for the asset.
            """
            file_path = filedialog.askopenfilename(
                title="Select image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*"),
                ],
            )
            if file_path:
                self.image_path_var.set(file_path)

        browse_btn = ctk.CTkButton(
            img_row_frame,
            text="Browse...",
            width=80,
            command=browse_image_edit,
        )
        browse_btn.grid(row=0, column=1)

        # Row 12: Available checkbox
        chk = ctk.CTkCheckBox(frame, text="Available", variable=self.available_var)
        chk.grid(row=12, column=0, columnspan=2, sticky="w", pady=6)

        # Buttons at bottom of dialog
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Changes",
            command=lambda: self.save_edited_asset(win, row["ASSET_ID"]),
        )
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", command=win.destroy)
        cancel_btn.pack(side="right")

    def save_edited_asset(self, window, asset_id):
        """
        Read the edit-asset form, validate, and update the asset record.
        """
        description = self.description_var.get().strip() or None
        brand = self.brand_var.get().strip() or None
        model = self.model_var.get().strip() or None
        serial = self.serial_var.get().strip() or None
        purchase_date = self.purchase_date_var.get().strip() or None
        site = self.site_var.get().strip() or None
        location = self.location_var.get().strip() or None
        dept = self.dept_var.get().strip() or None
        category = self.category_var.get().strip() or None
        image_path = self.image_path_var.get().strip() or None
        available = self.available_var.get()

        cost_value = None
        cost_str = self.cost_var.get().strip()
        if cost_str:
            try:
                cost_value = float(cost_str)
            except ValueError:
                print("Cost must be a number.")
                return

        try:
            update_asset(
                asset_id=asset_id,
                description=description,
                brand=brand,
                model=model,
                serial=serial,
                purchase_date=purchase_date,
                cost=cost_value,
                site_name=site,
                location_name=location,
                dept_name=dept,
                category_name=category,
                image_path=image_path,
                available=available,
                acting_emp_id=self.acting_emp_id,
            )
        except Exception as e:
            print("Error updating asset:", e)
            return

        window.destroy()
        self.refresh_table()

    # ============================================================
    # Delete asset
    # ============================================================

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

    # ============================================================
    # Maintenance dialog
    # ============================================================

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

        info_lbl = ctk.CTkLabel(
            frame,
            text=f"Asset ID: {self.selected_asset_id}\nEnter maintenance notes below:",
            justify="left",
        )
        info_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.maint_text = ctk.CTkTextbox(frame, height=180)
        self.maint_text.grid(row=1, column=0, sticky="nsew")

        status_lbl = ctk.CTkLabel(frame, text="")
        status_lbl.grid(row=2, column=0, sticky="w", pady=(5, 0))

        def save_maintenance():
            """
            Save the maintenance note to the database and close the dialog.
            """
            note = self.maint_text.get("1.0", "end").strip()
            if not note:
                status_lbl.configure(text="Maintenance note cannot be empty.", text_color="red")
                return

            try:
                add_maintenance_entry(
                    asset_id=self.selected_asset_id,
                    emp_id=self.acting_emp_id,
                    note=note,
                )
            except Exception as e:
                status_lbl.configure(text=str(e), text_color="red")
                return

            status_lbl.configure(text="Maintenance entry saved.", text_color="green")
            win.after(600, win.destroy)

        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(btn_frame, text="Save", command=save_maintenance)
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", command=win.destroy)
        cancel_btn.pack(side="right")
